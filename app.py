import os
from flask import Flask
from flask_migrate import Migrate

from config import Config
from models import db
from routes import register_routes
from utils.helpers import register_template_filters, ensure_upload_directory

def create_app(config_class=Config):
    """Flask uygulamasını oluşturur ve konfigüre eder."""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Veritabanını başlat
    db.init_app(app)
    Migrate(app, db)
    
    # Yükleme klasörünün varlığını kontrol et
    with app.app_context():
        ensure_upload_directory(app)
    
    # Şablon filtrelerini kaydet
    register_template_filters(app)
    
    # Route'ları kaydet
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=True
    )
