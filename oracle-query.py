# Django REST Framework Project Deployment Guide

## 🚀 Project Overview
This guide covers deploying a Django REST Framework project to Render, with a focus on free-tier deployment and best practices.

## 📋 Prerequisites
- Python 3.10+
- Django 4.2+
- Git
- Render Account
- GitHub Account

## 🛠 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/your-project.git
cd your-project
```

### 2. Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file for local development:
```
SECRET_KEY=your-local-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 🌐 Deployment Preparation

### 1. Project Structure
```
your_project/
├── manage.py
├── requirements.txt
├── build.sh (or build.bat)
├── common/
│   ├── settings.py
│   └── ...
├── app/
│   ├── models.py
│   └── ...
└── .gitignore
```

### 2. Required Files

#### `requirements.txt`
```
Django==4.2.6
djangorestframework==3.14.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
whitenoise==6.5.0
python-dotenv==1.0.0
```

#### `build.sh` (Unix/Render Preferred)
```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

#### `runtime.txt`
```
python-3.10.12
```

### 3. Settings Configuration
Key modifications in `common/settings.py`:
```python
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Security and Deployment Settings
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🔧 Render Deployment Steps

### 1. GitHub Preparation
```bash
git init
git add .
git commit -m "Prepare for Render deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Render Web Service Setup
1. Log into Render (https://render.com)
2. Click "New +" > "Web Service"
3. Connect your GitHub repository

#### Deployment Configuration
- Name: your-project-name
- Branch: main
- Build Command: `./build.sh`
- Start Command: `gunicorn common.wsgi:application`

### 3. Environment Variables
Add in Render Web Service dashboard:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: From Render PostgreSQL service
- `PYTHON_VERSION`: 3.10.12
- `DEBUG`: False

### 4. PostgreSQL Database
1. Create PostgreSQL service in Render
2. Copy "Internal Database URL"
3. Use as `DATABASE_URL` in Web Service

## 🛡 Security Best Practices
- Never commit sensitive information
- Use environment variables
- Regularly update dependencies
- Enable Django's security features

## 🔍 Troubleshooting

### Common Deployment Issues
- Verify `ALLOWED_HOSTS`
- Check database configuration
- Ensure all dependencies installed
- Review Render build logs

### Debugging Checklist
- ✅ Requirements file complete
- ✅ Build script executable
- ✅ Environment variables set
- ✅ Static files configured
- ✅ Database connection working

## 📚 Additional Resources
- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [DRF Best Practices](https://www.django-rest-framework.org/topics/best-practices/)

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Disclaimer**: Free-tier hosting has limitations. Consider upgraded services for production-critical applications.
```

This README provides a comprehensive guide that:
- Explains the entire deployment process
- Provides code snippets
- Offers troubleshooting advice
- Includes best practices

Would you like me to modify anything to make it more specific to your project?

Key features:
- Step-by-step instructions
- Code examples
- Troubleshooting section
- Security considerations
- Resource links</antArtifact>
