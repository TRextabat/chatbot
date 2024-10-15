from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel, ActivatorModel
from utils.model_abstracts import Model
import uuid


class PDFDocument(Model, 
                  TimeStampedModel, 
                  TitleDescriptionModel, 
                  ActivatorModel
                  ):
    """
    Modle to store the PDF document and parsed text
    """
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/pdfs/')
    parsed_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return rf"title:{self.title} - ID:{self.id}"
    
class PDFVectorEmbedding(Model, 
                         TimeStampedModel, 
                         ActivatorModel
                         ):
    """
    Model to store the vector embeddings of the PDF document
    """
    pdf = models.OneToOneField(PDFDocument, on_delete=models.CASCADE)
    vector = ArrayField(models.FloatField())

    def __str__(self):
        return rf"PDF:{self.pdf.title} - ID:{self.id}"