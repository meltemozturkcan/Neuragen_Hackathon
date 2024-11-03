import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from db_config import DB_CONFIG


def create_database():
    try:
        # Önce postgres veritabanına bağlanıyoruz
        connection = psycopg2.connect(user="member1",
                                  password="member1pass",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="neuragendev")
        
#        connection = psycopg2.connect(
#            user=DB_CONFIG['user'],
#            password=DB_CONFIG['password'],
#            host=DB_CONFIG['host'],
#            port=DB_CONFIG['port']
#        )
        
        if(connection is None):
            print("CONNECTION IS NONE")

        print("CONNECTION IS OKAY")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()

        # Önce veritabanının var olup olmadığını kontrol edelim
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'neuragendev'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute('CREATE DATABASE neuragendev')
            print("Veritabanı başarıyla oluşturuldu!")
        else:
            print("Veritabanı zaten mevcut!")

    except (Exception, Error) as error:
        print("Hata:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


def create_tables():
    try:
        # Yeni oluşturulan veritabanına bağlanıyoruz
        connection = psycopg2.connect(
            dbname="neuragendev",
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        cursor = connection.cursor()

        # Kullanıcılar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(25) NOT NULL,
                surname VARCHAR(50) NOT NULL,
                birth_year INTEGER NOT NULL,
                school_grade VARCHAR(25) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            ) 
         """)
        
        print("user passed")
        
        #Prompt Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt (
                id SERIAL PRIMARY KEY,
                prompt TEXT,
                model_name VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
        """)
        
        print("prompt passed")

        #Gemini_Response_Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gemini_response (
                id SERIAL PRIMARY KEY,
                pronunciation_score FLOAT,
                areas_of_improvement TEXT,
                vowel TEXT,
                consonant TEXT,
                clarity TEXT,
                confidence_score FLOAT,
                prompt TEXT,
                model_name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
        """)

        # Test sonuçları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                letter_id INTEGER REFERENCES turkish_alphabet(id),
                gemini_response_id INTEGER REFERENCES gemini_response(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
        """)

        # Test kelimeler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turkish_alphabet (
                id SERIAL PRIMARY KEY,
                letter VARCHAR(100) NOT NULL,
                difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
                category VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Kullanıcı istatistikleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                total_tests INTEGER DEFAULT 0,
                average_pronunciation_score FLOAT DEFAULT 0.0,
                avg_clarity FLOAT DEFAULT 0.0,
                last_test_date TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_user_stats
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE)
        """)

        # Değişiklikleri kaydediyoruz
        connection.commit()
        print("Tablolar başarıyla oluşturuldu!")

    except (Exception, Error) as error:
        print("Hata:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    print("BEFORE CREATE DB")
    create_database()
    print("after create db")
    create_tables()