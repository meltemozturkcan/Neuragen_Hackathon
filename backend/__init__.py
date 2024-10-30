from flask import Flask
from config import config
from database.db_config import get_db_connection


def create_app(config_name='default'):
    app = Flask(__name__)

    # Konfigürasyonu yükle
    app.config.from_object(config[config_name])

    # Veritabanı bağlantısını test et
    with app.app_context():
        conn = get_db_connection()
        if conn:
            print("Veritabanı bağlantısı başarılı!")
            conn.close()

    return app