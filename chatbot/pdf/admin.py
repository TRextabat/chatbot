from django.contrib import admin
from .models import PDFDocument, PDFVectorEmbedding


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'modified', 'status', 'status_changed')
    search_fields = ('title', 'description')
    list_filter = ('status', 'created', 'modified', 'status_changed')
    readonly_fields = ('id', 'parsed_text', 'created', 'modified', 'status_changed')