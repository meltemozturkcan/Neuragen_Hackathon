import os
from dotenv import load_dotenv
import psycopg2

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
    },
    'externalUser': {"connectionString":"postgresql://neuragendevv_user:mm5UoVZRi337bfhp2k2KBZY7Odt0BPFP@dpg-csjjrhi3esus7385rpv0-a.oregon-postgres.render.com/neuragendevv"},
    'internalUser': {"connectionString":"postgresql://neuragendevv_user:mm5UoVZRi337bfhp2k2KBZY7Odt0BPFP@dpg-csjjrhi3esus7385rpv0-a/neuragendevv"}
    }

# Aktif konfigürasyonu .env dosyasından al
# ACTIVE_MEMBER = os.getenv('TEAM_MEMBER', 'member1')
ACTIVE_MEMBER = "internalUser" #"member1"

# Aktif üyenin konfigürasyonunu kullan
DB_CONFIG = TEAM_CONFIGS.get(ACTIVE_MEMBER)

def get_db_connection():
    try:
        if DB_CONFIG.get("connectionString"):
            #connectionString = DB_CONFIG.get("connectionString")
            connection = psycopg2.connect(DB_CONFIG.get("connectionString"))
            print("# db_config ## INTERNAL get_db_connection(): Connection sağlandı")
            return connection
        
        connection = psycopg2.connect(**DB_CONFIG)
        print("# db_config ## get_db_connection(): Connection sağlandı")
        return connection
    
    except psycopg2.Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None