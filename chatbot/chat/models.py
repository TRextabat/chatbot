from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel, ActivatorModel
from utils.model_abstracts import Model

class ChatSession(Model,
                  TimeStampedModel,
                  ActivatorModel,
                  TitleDescriptionModel
                  ):
    
    is_active = models.BooleanField(default=True, help_text="Indicates if the session is active")
    pdf_documents = models.ManyToManyField('pdf.PDFDocument', related_name="chat_sessions")
    
    class Meta:
        indexes = [
            models.Index(fields=["is_active", "modified"]),
        ]

    def __str__(self):
        return f"ChatSession: {self.title} (ID: {self.id})"


class ChatMassage(TimeStampedModel):

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    message_text = models.TextField(help_text="The content of the message.")
    is_bot_response = models.BooleanField(default=False, help_text="True if this is a bot response")

    class Meta:
        indexes = [
            models.Index(fields=["session", "created"]),
        ]
    
    def __str__(self):
        return f"ChatMessage by {self.sender} in Session ID: {self.session.id}"