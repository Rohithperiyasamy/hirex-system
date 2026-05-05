"""
Django settings for Hirex project.
AI-Powered Automated Technical Interview Platform
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────
SECRET_KEY    = os.getenv('SECRET_KEY', 'django-insecure-hirex-change-this-in-production-xyz123')
DEBUG         = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ── APPS ──────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Authentication',
    'Myapp',
    'Hr',
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

ROOT_URLCONF = 'Hirex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'Templates')],
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

WSGI_APPLICATION = 'Hirex.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

STATIC_URL       = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT      = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── EMAIL ─────────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = os.getenv('EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT          = int(os.getenv('EMAIL_PORT', '587'))   # FIX 1: read from .env
EMAIL_USE_TLS       = True
EMAIL_USE_SSL       = False
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
# Add this line:
SERVER_EMAIL        = 'rohithperiyasamy74@gmail.com'# FIX 2: read directly from env, not from variable

# ── AI PROVIDER ───────────────────────────────────────────────────
AI_PROVIDER    = os.getenv('AI_PROVIDER', 'ollama')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OLLAMA_MODEL   = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
GEMINI_MODEL   = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# ── IOT ───────────────────────────────────────────────────────────
IOT_SECRET_KEY = os.getenv('IOT_SECRET_KEY', 'hirex-iot-secret-2025')

# ── BRANDING ──────────────────────────────────────────────────────
PLATFORM_NAME    = 'Hirex'
PLATFORM_TAGLINE = 'AI-Powered Automated Technical Interview Platform'
SUPPORT_EMAIL    = os.getenv('SUPPORT_EMAIL', 'support@hirex.ai')
COMPANY_NAME     = os.getenv('COMPANY_NAME', 'Hirex Technologies Pvt Ltd')