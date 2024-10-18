from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import logging
from .models import PDFDocument
from .serializers import validate_pdf_file
import os
class PDFDocumentModelTest(TestCase):

    def test_create_pdf_document(self):
        """
        Test that a PDFDocument can be created with a valid title and file.
        """
        pdf_file = SimpleUploadedFile("Back_end_takehome.pdf", b"file_content", content_type="application/pdf")
        
        # Create the PDFDocument instance
        pdf_document = PDFDocument.objects.create(
            title="Test PDF",
            file=pdf_file
        )
        
        self.assertEqual(pdf_document.title, "Test PDF")
        self.assertTrue(os.path.basename(pdf_document.file.name), "Back_end_takehome.pdf")

    def test_pdf_document_str(self):
        """
        Test the string representation of the PDFDocument.
        """
        pdf_file = SimpleUploadedFile("Back_end_takehome.pdf", b"file_content", content_type="application/pdf")
        pdf_document = PDFDocument.objects.create(title="Test PDF", file=pdf_file)
        
        # Expected format for the string representation
        expected_str = f"title: {pdf_document.title} - ID: {pdf_document.id}"
        self.assertEqual(str(pdf_document), expected_str)

class PDFFileValidatorTest(TestCase):

    def test_valid_pdf_file(self):
        # Create a valid PDF file
        pdf_file = SimpleUploadedFile("Back_end_takehome.pdf", b"file_content", content_type="application/pdf")
        
        # Should pass without raising a ValidationError
        validate_pdf_file(pdf_file)

    def test_invalid_file_extension(self):
        invalid_file = SimpleUploadedFile("Back_end_takehome.txt", b"file_content", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_pdf_file(invalid_file)

    def test_file_too_large(self):
        # Simulate a file larger than the max allowed size
        large_file = SimpleUploadedFile("large.pdf", b"a" * (100 * 1024 * 1024), content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_pdf_file(large_file)


class PDFUploadTest(APITestCase):

    def setUp(self):
        self.url = reverse('pdf')

        self.logger = logging.getLogger('your_app_name')  # Replace with your app's logger name
        self.logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture detailed logs
        self.log_stream = logging.StreamHandler()  # Output logs to the console
        self.logger.addHandler(self.log_stream)


    def test_valid_pdf_upload(self):
        """
        Ensure we can upload a valid PDF document.
        """
        # Create a simple mock PDF file
        pdf_file = SimpleUploadedFile(
            "test.pdf", b"dummy content", content_type="application/pdf"
        )

        data = {
            'title': 'Test PDF',
            'file': pdf_file
        }

        # Perform a POST request
        response = self.client.post(self.url, data, format='multipart')
        self.logger.debug("Starting test_valid_pdf_upload")
        self.logger.debug(f"Response status code: {response.status_code}")
        self.logger.debug(f"Response data: {response.data}")


        # Log the response content for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {response.data}")

        # Check the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Verify the document is in the database
        self.assertEqual(PDFDocument.objects.count(), 1)
        pdf_document = PDFDocument.objects.first()
        self.assertEqual(pdf_document.title, 'Test PDF')

    def test_invalid_file_upload(self):
        """
        Ensure that an invalid file (not a PDF) raises a validation error.
        """
        # Create a dummy text file
        txt_file = SimpleUploadedFile(
            "test.txt", b"This is a text file.", content_type="text/plain"
        )
        data = {
            'title': 'Invalid File',
            'file': txt_file
        }

        # Perform a POST request
        response = self.client.post(self.url, data, format='multipart')

        # Check that the request fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_without_file(self):
        """
        Ensure that uploading without a file raises a validation error.
        """
        # Perform a POST request without a file
        
        response = self.client.post(self.url, {}, format='multipart')

        # Check that the request fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        self.logger
