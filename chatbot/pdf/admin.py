from django.contrib import admin
from .models import PDFDocument, PDFVectorEmbedding


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'modified', 'status')
    search_fields = ('title', 'description')