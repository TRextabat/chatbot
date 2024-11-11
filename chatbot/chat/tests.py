from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from chat.models import ChatSession, ChatMassage
from pdf.models import PDFDocument
from unittest.mock import patch, MagicMock, AsyncMock
import uuid

class ChatSessionTests(APITestCase):

    def setUp(self):
        self.pdf_document = PDFDocument.objects.create(title="Test PDF", file="path/to/test.pdf")
        self.chat_session_data = {
            "title": "Test Session",
            "description": "Test Description",
            "pdf_documents": [self.pdf_document.id]
        }
        self.chat_session = ChatSession.objects.create(
            title="Test Session",
            description="Test Description"
        )
        self.chat_session.pdf_documents.add(self.pdf_document)

    @patch('chat.views.LlamaServiceManager.get_service')
    def test_create_chat_session(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.initialize_session = AsyncMock()
        mock_get_service.return_value = mock_service
        url = reverse('start_chat_session')
        response = self.client.post(url, self.chat_session_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatSession.objects.count(), 2)
        self.assertEqual(response.data['title'], self.chat_session_data['title'])

    @patch('chat.views.LlamaServiceManager.get_service')
    def test_get_chat_sessions(self, mock_get_service):
        url = reverse('start_chat_session')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('chat.views.LlamaServiceManager.get_service')
    def test_activate_chat_session(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.initialize_session = AsyncMock()
        mock_get_service.return_value = mock_service
        url = reverse('chatsession-action', args=['activate', self.chat_session.id])
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ChatSession.objects.get(id=self.chat_session.id).is_active)

    @patch('chat.views.LlamaServiceManager.get_service')
    def test_deactivate_chat_session(self, mock_get_service):
        url = reverse('chatsession-action', args=['deactivate', self.chat_session.id])
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ChatSession.objects.get(id=self.chat_session.id).is_active)

class ChatInteractiveTests(APITestCase):

    def setUp(self):
        self.pdf_document = PDFDocument.objects.create(title="Test PDF", file="path/to/test.pdf")
        self.chat_session = ChatSession.objects.create(
            title="Test Session",
            description="Test Description"
        )
        self.chat_session.pdf_documents.add(self.pdf_document)
        self.message_data = {
            "message_text": "Hello, chatbot!"
        }

    @patch('chat.views.LlamaServiceManager.get_service')
    def test_interact_with_chat_session(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.agent_query = AsyncMock(return_value="Hello, user!")
        mock_get_service.return_value = mock_service
        url = reverse('chat_interactive', args=[self.chat_session.id])
        response = self.client.post(url, self.message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatMassage.objects.count(), 2)
        self.assertEqual(response.data['message_text'], "Hello, user!")
