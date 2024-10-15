from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import PDFDocument, PDFVectorEmbedding
from dotenv import load_dotenv
import os
import re

load_dotenv()

def validate_pdf_file(value):

    extension = os.path.splitext(value.name)[1].lower()
    if extension != '.pdf':
        raise ValidationError({"file": "Invalid file type. Please upload a PDF file."})
    
    max_size = int(os.environ.get("MAX_PDF_SIZE"))
    if value.size > max_size:
        raise ValidationError({"file": f"File size exceeds the maximum limit {max_size}."})
    
    # Clean the file name to remove special characters
    cleaned_name = re.sub(r'[^\w\d\-_\.]', '_', value.name)
    value.name = cleaned_name
    return value

class PDFDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_pdf_file])

    class Meta:
        model = PDFDocument
        fields = [
            'id', 'title', 'description', 'file', 'parsed_text', 
            'created', 'modified', 'status', 'status_changed'
        ]
        read_only_fields = ['id', 'parsed_text', 'created', 'modified', 'status_changed']
    
    def validate_title(self, value):
        if len(value) > 255:
            raise serializers.ValidationError('Title cannot exceed 255 characters.')
        return value


class PDFVectorEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFVectorEmbedding
        fields = ['id', 'pdf', 'vector', 
                  'created', 'modified', 'status', 
                  'status_changed']
        
        read_only_fields = ['id', 'created', 
                            'modified', 'status_changed']
        
        def validate_vector(self, value):
            if not isinstance(value, list):
                raise serializers.ValidationError("Vector must be a list of float values.")
            
            if not all(isinstance(v, float) for v in value):
                raise serializers.ValidationError('All elements in the vector must be floats.')
        
            return value
        