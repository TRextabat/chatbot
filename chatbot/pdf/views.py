from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from .models import PDFDocument
from .serializers import PDFDocumentSerializer
import logging

logger = logging.getLogger(__name__)

class PDFDocumentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PDF(views.APIView):
    
    def post(self, request):

        try:
            request.upload_handlers.insert(0, TemporaryFileUploadHandler(request=request))
            serializer = PDFDocumentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.title, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

