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
    PDFDocument model represents a PDF file with associated metadata.

    Attributes:
        title (CharField): The title of the PDF document.
        file (FileField): The file field to upload the PDF document.
        parsed_text (TextField): The parsed text content of the PDF document, can be blank or null.

    Methods:
        __str__(): Returns a string representation of the PDFDocument instance, including the title and ID.
    """

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/pdfs/')
    parsed_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return rf"title: {self.title} - ID: {self.id}"
    
class PDFVectorEmbedding(Model, 
                        
                         TimeStampedModel, 
                         ActivatorModel
                         ):
    """
    PDFVectorEmbedding is a Django model that represents a vector embedding for a PDF document.
    Attributes:
        pdf (OneToOneField): A one-to-one relationship with the PDFDocument model. 
                                When the associated PDFDocument is deleted, this model instance will also be deleted.
        vector (ArrayField): An array field that stores a list of float values representing the vector embedding of the PDF document.
    Methods:
        __str__(): Returns a string representation of the PDFVectorEmbedding instance, 
                    including the title of the associated PDF document and the ID of the embedding.
    """
    
    pdf = models.OneToOneField(PDFDocument, on_delete=models.CASCADE)
    vector = ArrayField(models.FloatField())

    def __str__(self):
        return rf"PDF:{self.pdf.title} - ID:{self.id}"