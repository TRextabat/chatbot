from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from drf_yasg.utils import swagger_auto_schema
from .models import PDFDocument
from .serializers import PDFDocumentSerializer
import logging

logger = logging.getLogger(__name__)

class PDFDocumentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PDF(views.APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Upload a PDF document",
        request_body=PDFDocumentSerializer,
        responses={status.HTTP_201_CREATED: PDFDocumentSerializer}
    )
    def post(self, request):
        logger.info("Received POST request for PDF upload")
        logger.debug(f"Request data: {request.data}")

        try:
            request.upload_handlers.insert(0, TemporaryFileUploadHandler(request=request))
            logger.info("TemporaryFileUploadHandler added")

            serializer = PDFDocumentSerializer(data=request.data)
            logger.debug("Serializer initialized for PDFDocument")

            if serializer.is_valid():
                logger.info("Serializer validated successfully")
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning("Serializer validation failed")
                logger.debug(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}", exc_info=True)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

