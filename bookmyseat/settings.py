import os
from pathlib import Path
import dj_database_url

# 1. Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-c8aetlj(=vp90n@#yoc^&d(_6ivp(d!bv-4-f!r$lawptjzrwu')
DEBUG = True # Vercel par error dekhne ke liye True rakhein, baad mein False kar dena
ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'localhost']

# 3. Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'movies',
    'dashboard',
]

# 4. Middleware (Whitenoise is MUST for Vercel)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5. Razorpay Configuration (Use Environment Variables)
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

ROOT_URLCONF = 'bookmyseat.urls'
WSGI_APPLICATION = 'bookmyseat.wsgi.application'

# 6. Database (Render Postgres)
DATABASES = {
    'default': dj_database_url.parse('postgresql://book_myseat_clone_user:AOTC3XEcTK13Bjk20aFR5BYOZH1faX4S@dpg-d65gof1r0fns73d3u9pg-a.virginia-postgres.render.com/book_myseat_clone')
}

# 7. Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# 8. Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 9. Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'add.mail.user0@gmail.com'
EMAIL_HOST_PASSWORD = 'gatjdcrfxkgwmlra' # Note: Use App Password

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL='/login/'