import os
from dotenv import load_dotenv

# .env dosyasını yükle (eğer varsa)
load_dotenv()

class Config:
    """Uygulama konfigürasyon ayarları."""
    
    # Flask ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gelistir-ve-degistir-bu-anahtari'
    PORT = int(os.environ.get('PORT', 5023))
    
    # SQLite veritabanı yolu
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASEDIR, "prompt_archive.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dosya yükleme ayarları
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'wav'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Sayfalama ayarları
    ITEMS_PER_PAGE = 10
