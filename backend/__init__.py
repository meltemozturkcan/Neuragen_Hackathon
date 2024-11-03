from flask import Flask
from config import config
from database.db_config import get_db_connection
from flask_cors import CORS
from database import user_operations
from backend import alphabet_operations, gemini_response_operations, user_stats_operations, test_api_operations


def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)

    # Konfigürasyonu yükle
    app.config.from_object(config[config_name])
    app.register_blueprint(user_operations.bp)
    app.register_blueprint(alphabet_operations.alphabet_bp)
    app.register_blueprint(gemini_response_operations.gemini_response_bp)
    app.register_blueprint(user_stats_operations.user_stats_bp)
    app.register_blueprint(test_api_operations.test_api__bp)

    # Veritabanı bağlantısını test et
    with app.app_context():
        conn = get_db_connection()
        if conn:
            print("# backend/__init__py ## create_app(): Veritabanı bağlantısı başarılı!")
            conn.close()

    return app



