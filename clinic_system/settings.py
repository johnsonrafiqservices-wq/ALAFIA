"""
Django settings for clinic_system project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.3', '127.0.0.1', '172.16.61.154','192.168.100.5', '172.16.61.129']


# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For intcomma and other number formatting filters
    'crispy_forms',
    'clinic_settings',
    'crispy_bootstrap5',
    'widget_tweaks',
    'accounts',
    'patients',
    'appointments',
    'billing',
    'medical_records',
    'reports',
    'inventory',
    'laboratory',
    'pharmacy',
    'budget',
    'django_celery_beat',
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

ROOT_URLCONF = 'clinic_system.urls'

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
                'clinic_settings.context_processors.clinic_settings',
                'clinic_settings.context_processors.modal_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'clinic_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/patients/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Role-based access control
ROLES = {
    'admin': 'Administrator',
    'doctor': 'Doctor/Physiotherapist',
    'nutritionist': 'Nutritionist',
    'receptionist': 'Receptionist',
    'nurse': 'Nurse',
    'billing': 'Billing Staff',
    'patient': 'Patient'
}

# ==================== EMAIL / SMTP SETTINGS ====================
# Configure Gmail SMTP via environment variables. Use an App Password for Gmail.
# Example env vars:
#   EMAIL_HOST_USER=youraddress@gmail.com
#   EMAIL_HOST_PASSWORD=your_gmail_app_password
#   DEFAULT_FROM_EMAIL=youraddress@gmail.com
#
# For testing/development, set EMAIL_BACKEND=console to print emails to console
# For production, set EMAIL_BACKEND=smtp to send real emails
EMAIL_BACKEND_TYPE = os.getenv('EMAIL_BACKEND', 'smtp')  # 'smtp' or 'console'

if EMAIL_BACKEND_TYPE == 'console':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = (os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true')
EMAIL_USE_SSL = (os.getenv('EMAIL_USE_SSL', 'false').lower() == 'true')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'alafiapoint@gmail.com')
# IMPORTANT: Gmail App Passwords must not contain spaces. Remove spaces from the UI string.
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'wicu bviv dnrb lxzt')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'alafiapoint@gmail.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 20))

# Gmail Setup Instructions:
# 1. Enable 2-Step Verification in your Google Account
# 2. Go to https://myaccount.google.com/apppasswords
# 3. Generate an App Password for "Mail"
# 4. Use that 16-character password (without spaces) as EMAIL_HOST_PASSWORD
# 5. Make sure "Less secure app access" is NOT needed for App Passwords

# SMS Service Configuration
# Supports: africas_talking, peoples_sms, smsbox, generic
SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'africas_talking')

# Africa's Talking (Recommended for Uganda/East Africa)
AFRICAS_TALKING_API_KEY = os.getenv('AFRICAS_TALKING_API_KEY', '')
AFRICAS_TALKING_USERNAME = os.getenv('AFRICAS_TALKING_USERNAME', 'sandbox')

# People's SMS Uganda
PEOPLES_SMS_API_KEY = os.getenv('PEOPLES_SMS_API_KEY', '')
PEOPLES_SMS_SENDER_ID = os.getenv('PEOPLES_SMS_SENDER_ID', '')

# SMS Box Uganda
SMSBOX_API_KEY = os.getenv('SMSBOX_API_KEY', '')
SMSBOX_SENDER_ID = os.getenv('SMSBOX_SENDER_ID', '')

# Generic HTTP SMS Gateway
GENERIC_SMS_URL = os.getenv('GENERIC_SMS_URL', '')
GENERIC_SMS_API_KEY = os.getenv('GENERIC_SMS_API_KEY', '')
GENERIC_SMS_SENDER_ID = os.getenv('GENERIC_SMS_SENDER_ID', '')

# Django Jet Reboot Configuration
JET_DEFAULT_THEME = 'default'
JET_THEMES = [
    {
        'theme': 'default',
        'color': '#47bac1',
        'title': 'Default'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#ecf2f6',
        'title': 'Light Gray'
    },
   
]

JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = False
# JET_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomIndexDashboard'
# JET_APP_INDEX_DASHBOARD = 'clinic_system.dashboard.CustomAppIndexDashboard'

# Disable custom menu to avoid KeyError
# JET_SIDE_MENU_ITEMS will use Django Jet's default auto-generated menu

# ==================== CELERY CONFIGURATION ====================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Send birthday wish emails every day at 08:00 server time
    'send-birthday-wishes-daily': {
        'task': 'patients.tasks.send_birthday_wishes',
        'schedule': crontab(hour=8, minute=0),
    },
}
