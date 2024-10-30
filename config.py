import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """Temel konfigürasyon sınıfı"""

    # Veritabanı ayarları
    DB_NAME = os.getenv('DB_NAME', 'neuragendev')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask ayarları
    SECRET_KEY = os.getenv('SECRET_KEY', 'gelistirme-anahtari')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Gemini API ayarları
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Uygulama ayarları
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))


class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    """Üretim ortamı konfigürasyonu"""
    DEBUG = False
    DEVELOPMENT = False


# Konfigürasyon sözlüğü
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}