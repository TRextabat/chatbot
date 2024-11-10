from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from .models import ChatSession, ChatMassage
from .serializers import ChatSessionSerializer, ChatSessionHistorySerializer, ChatMassageSerializer, ChatMessageRequestSerializer
from .tasks import insert_messages
from pdf.models import PDFDocument
from services.ollama import LlamaServiceManager
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from asgiref.sync import sync_to_async
import logging
import asyncio

logger = logging.getLogger('chat')

class ChatSessionView(APIView):

    serializer_class = ChatSessionSerializer
    
    @swagger_auto_schema(
        request_body=ChatSessionSerializer,
        responses={
            201: openapi.Response('Created', ChatSessionSerializer),
            400: 'Bad Request'
        }
    )
    def post(self, request):
        data = request.data  
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            chat_session = serializer.save()
            # Get PDF documents from the request
            pdf_ids = data.get('pdf_documents', [])
            pdfs = PDFDocument.objects.filter(id__in=pdf_ids)
            pdf_paths = [pdf.file.path for pdf in pdfs]

            # Initialize LlamaService for the new chat session
            service = LlamaServiceManager.get_service(chat_session.id)
            chat_history = []  # Initial chat history
            asyncio.run(service.initialize_session(pdfs=pdf_paths, chat_history=chat_history))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('datetime', openapi.IN_QUERY, description="Filter by datetime", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
            openapi.Parameter('number', openapi.IN_QUERY, description="Limit number of results", type=openapi.TYPE_INTEGER),
            openapi.Parameter('history', openapi.IN_QUERY, description="Include chat history", type=openapi.TYPE_BOOLEAN)
        ],
        responses={
            200: openapi.Response('OK', ChatSessionSerializer(many=True)),
            400: 'Bad Request'
        }
    )
    def get(self, request):

        datetime_str = request.query_params.get('datetime')
        number = request.query_params.get('number')
        include_history = request.query_params.get('history', 'false').lower() == 'true'

        filters = Q()
        if datetime_str:
            datetime_obj = parse_datetime(datetime_str)
            if datetime_obj:
                filters &= Q(created__gte=datetime_obj)

        chat_sessions = ChatSession.objects.filter(filters).order_by('-created')
        if number:
            chat_sessions = chat_sessions[:int(number)]

        if include_history:
            serializer = ChatSessionHistorySerializer(chat_sessions, many=True)
        else:
            serializer = ChatSessionSerializer(chat_sessions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ChatSessionActionView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('action', openapi.IN_PATH, description="Action to perform (activate/deactivate)", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK', ChatSessionSerializer),
            404: 'Not Found',
            400: 'Bad Request'
        }
    )
    def patch(self, request, action, session_id):
        try:
            chat_session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            raise NotFound(detail="Chat session not found")
        
        match action:
            case 'activate':
                chat_session.is_active = True
                chat_session.save()
                # Initialize LlamaService for the chat session
                service = LlamaServiceManager.get_service(chat_session.id)
                pdf_paths = [pdf.file.path for pdf in chat_session.pdf_documents.all()]
                chat_history = []  # Initial chat history
                asyncio.run(service.initialize_session(pdfs=pdf_paths, chat_history=chat_history))
            case 'deactivate':
                chat_session.is_active = False
                chat_session.save()
                LlamaServiceManager.delete_service(chat_session.id)
            case _:
                raise ValidationError(detail="Invalid action")
            
        serializer = ChatSessionSerializer(chat_session)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChatInteractiveView(APIView):

    @swagger_auto_schema(
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message_text': openapi.Schema(type=openapi.TYPE_STRING, description='The message text')
            },
            required=['message_text']
        ),
        responses={
            201: openapi.Response(
                description='Created',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'session': openapi.Schema(type=openapi.TYPE_STRING, description='Session ID'),
                        'message_text': openapi.Schema(type=openapi.TYPE_STRING, description='The message text'),
                        'is_bot_response': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is this a bot response'),
                        'created': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Creation time'),
                        'modified': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Modification time')
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )    
    def post(self, request, session_id):
        try:
            chat_session = ChatSession.objects.get(id=session_id)
            logger.info(f"LOGWANT:Chat session found: {chat_session}")
        except ChatSession.DoesNotExist:
            return Response({"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND)


        message_text = request.data.get('message_text')
       
        llama_service = LlamaServiceManager.get_service(session_id)

        # Process the user message with the LlamaService
        logger.info(f"LOGWANT:Processing user message: {message_text}")
        try:
            response_text = asyncio.run(llama_service.agent_query(message_text))
            logger.info(f"LOGWANT:Response from LlamaService: {response_text}")
        except Exception as e:
            logger.error(f"LOGWANT:Error processing message with LlamaService: {e}")
            return Response({"error": "Error processing message with LlamaService"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_message_data = {
            "session": chat_session.id,
            "message_text": message_text,
            "is_bot_response": False
        }
        user_message_serializer = ChatMassageSerializer(data=user_message_data)
        user_message_serializer.is_valid(raise_exception=True)
        user_message_serializer.save()

        bot_message_data = {
            "session": chat_session.id,
            "message_text": str(response_text),
            "is_bot_response": True
        }
        bot_message_serializer = ChatMassageSerializer(data=bot_message_data)
        bot_message_serializer.is_valid(raise_exception=True)
        bot_message_serializer.save()

        return Response(bot_message_serializer.data, status=status.HTTP_201_CREATED)