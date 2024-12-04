# Additional requirements (add to requirements.txt)
anthropic==0.25.0

# Update claude_app/views.py
import os
import anthropic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClaudeQuerySerializer, ClaudeResponseSerializer

class ClaudeQueryView(APIView):
    def post(self, request):
        serializer = ClaudeQuerySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve Anthropic API key from environment
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                return Response(
                    {'error': 'Anthropic API key not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            
            # Create message to Claude
            question = serializer.validated_data['question']
            
            # Make API call
            message = client.messages.create(
                model="claude-3-opus-20240229",  # You can change the model as needed
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            
            # Extract the response
            response_text = message.content[0].text
            
            # Prepare response data
            response_data = {
                'response': response_text
            }
            
            response_serializer = ClaudeResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except anthropic.APIError as e:
            return Response(
                {'error': f'Anthropic API Error: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Optional: Add model selection to serializer
# claude_app/serializers.py
from rest_framework import serializers

class ClaudeQuerySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=True)
    model = serializers.ChoiceField(
        choices=[
            'claude-3-opus-20240229', 
            'claude-3-sonnet-20240229', 
            'claude-3-haiku-20240307'
        ],
        required=False,
        default='claude-3-opus-20240229'
    )

class ClaudeResponseSerializer(serializers.Serializer):
    response = serializers.CharField()

# Optional: Add some configuration to settings.py
# Add to claude_project/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ]
}

# Dockerfile (optional, for containerization)
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
