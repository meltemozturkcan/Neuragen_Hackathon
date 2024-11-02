import os
from dotenv import load_dotenv


load_dotenv()

# Takım üyelerinin local veritabanı ayarları
TEAM_CONFIGS = {
    'member1': {
        'dbname': 'neuragendev',
        'user': 'member1',
        'password': 'member1pass',
        'host': 'localhost',
        'port': '5432'
    },
    'member2': {
        'dbname': 'neuragendev',
        'user': 'member2',
        'password': 'member2pass',
        'host': 'localhost',
        'port': '5432'
    },
    'member3': {
        'dbname': 'neuragendev',
        'user': 'member3',
        'password': 'member3pass',
        'host': 'localhost',
        'port': '5432'
    }
}

# Aktif konfigürasyonu .env dosyasından al
# ACTIVE_MEMBER = os.getenv('TEAM_MEMBER', 'member1')
ACTIVE_MEMBER = "member1"

# Aktif üyenin konfigürasyonunu kullan
DB_CONFIG = TEAM_CONFIGS.get(ACTIVE_MEMBER)

def get_db_connection():
    import psycopg2
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except psycopg2.Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None