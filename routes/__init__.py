from routes.prompt_routes import prompt_bp
from routes.api_routes import api_bp

def register_routes(app):
    """Tüm blueprintleri Flask uygulamasına kaydeder."""
    app.register_blueprint(prompt_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
