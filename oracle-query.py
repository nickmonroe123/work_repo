# Project Structure:
# claude_api/
#   ├── manage.py
#   ├── claude_project/
#   │   ├── __init__.py
#   │   ├── settings.py
#   │   ├── urls.py
#   │   └── wsgi.py
#   ├── claude_app/
#   │   ├── __init__.py
#   │   ├── views.py
#   │   ├── serializers.py
#   │   ├── urls.py
#   │   └── models.py
#   └── requirements.txt

# requirements.txt
django==4.2.7
djangorestframework==3.14.0
requests==2.31.0
python-dotenv==1.0.0

# claude_project/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key-for-dev')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'claude_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'claude_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'claude_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# claude_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('claude_app.urls')),
]

# claude_app/serializers.py
from rest_framework import serializers

class ClaudeQuerySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=True)

class ClaudeResponseSerializer(serializers.Serializer):
    response = serializers.CharField()

# claude_app/views.py
import os
import requests
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
            # Note: This is a placeholder. Replace with actual Anthropic API interaction
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                return Response(
                    {'error': 'API key not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Actual Claude API call would look similar to this
            response_data = {
                'response': f"You asked: {serializer.validated_data['question']}"
            }
            
            response_serializer = ClaudeResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# claude_app/urls.py
from django.urls import path
from .views import ClaudeQueryView

urlpatterns = [
    path('claude/', ClaudeQueryView.as_view(), name='claude-query'),
]

# .env (create this file in the project root)
# DJANGO_SECRET_KEY=your-secret-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1
