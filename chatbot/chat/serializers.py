from rest_framework import serializers
from .models import ChatMassage, ChatSession
from pdf.models import PDFDocument



class ChatSessionSerializer(serializers.ModelSerializer):
    pdf_documents = serializers.PrimaryKeyRelatedField(
        queryset=PDFDocument.objects.all(), 
        many=True
    )


    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'description', 'is_active', 'pdf_documents', 'created', 'modified']
        read_only_fields = ['created', 'modified']

    

class ChatMassageSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=ChatSession.objects.all())

    class Meta:
        model = ChatMassage
        fields = [  'session','message_text', 'is_bot_response', 'created', 'modified']
        read_only_fields = ['created', 'modified']

class ChatMessageHistorySerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    content = serializers.CharField(source='message_text')

    class Meta:
        model = ChatMassage
        fields = ['role', 'content']

    def get_role(self, obj):
        return "bot" if obj.is_bot_response else "user"
    
class ChatSessionHistorySerializer(serializers.ModelSerializer):
    messages = ChatMessageHistorySerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'description', 'messages']

class ChatMessageRequestSerializer(serializers.Serializer):
    message_text = serializers.CharField()