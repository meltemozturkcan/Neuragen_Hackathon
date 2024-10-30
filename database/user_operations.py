import psycopg2
from psycopg2 import Error
import hashlib

class UserOperations:
    def __init__(self, db_config):
        self.db_config = db_config

    def hash_password(self, password):
        """Basit bir hash fonksiyonu"""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, email, password):
        """Veritabanına yeni kullanıcı ekler"""
        connection = None
        try:
            # Veritabanına bağlan
            connection = psycopg2.connect(**self.db_config)
            cursor = connection.cursor()

            # Şifreyi hashle
            hashed_password = self.hash_password(password)

            # SQL sorgusu
            insert_query = """
                INSERT INTO users (username, email, password_hash, is_active)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """

            # Sorguyu çalıştır
            cursor.execute(insert_query, (username, email, hashed_password, True))
            user_id = cursor.fetchone()[0]

            # Değişiklikleri kaydet
            connection.commit()
            print(f"Kullanıcı başarıyla eklendi. ID: {user_id}")
            return user_id

        except (Exception, Error) as error:
            print(f"Hata oluştu: {error}")
            if connection:
                connection.rollback()
            return None

        finally:
            if connection:
                cursor.close()
                connection.close()