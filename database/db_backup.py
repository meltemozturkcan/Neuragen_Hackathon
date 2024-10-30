import os
import subprocess
from datetime import datetime
from db_config import DB_CONFIG


def create_backup():
    """Veritabanının yedeğini alır"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.sql"
    backup_dir = "database/backups"

    # Backup dizini oluştur
    os.makedirs(backup_dir, exist_ok=True)

    backup_path = os.path.join(backup_dir, filename)

    try:
        # pg_dump ile yedek al
        subprocess.run([
            'pg_dump',
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-U', DB_CONFIG['user'],
            '-F', 'c',  # Custom format
            '-b',  # Binary format
            '-v',  # Verbose
            '-f', backup_path,
            DB_CONFIG['dbname']
        ], check=True)
        print(f"Yedekleme başarılı: {backup_path}")
    except subprocess.CalledProcessError as e:
        print(f"Yedekleme hatası: {e}")


def restore_backup(backup_file):
    """Veritabanını yedekten geri yükler"""
    try:
        # Önce mevcut bağlantıları kapat
        subprocess.run([
            'psql',
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-U', DB_CONFIG['user'],
            '-d', 'postgres',
            '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_CONFIG['dbname']}'"
        ], check=True)

        # Veritabanını yeniden oluştur
        subprocess.run([
            'dropdb',
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-U', DB_CONFIG['user'],
            DB_CONFIG['dbname']
        ], check=True)

        subprocess.run([
            'createdb',
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-U', DB_CONFIG['user'],
            DB_CONFIG['dbname']
        ], check=True)

        # Yedeği geri yükle
        subprocess.run([
            'pg_restore',
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-U', DB_CONFIG['user'],
            '-d', DB_CONFIG['dbname'],
            '-v',
            backup_file
        ], check=True)
        print("Geri yükleme başarılı!")
    except subprocess.CalledProcessError as e:
        print(f"Geri yükleme hatası: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) != 3:
            print("Kullanım: python db_backup.py restore <backup_file>")
            sys.exit(1)
        restore_backup(sys.argv[2])
    else:
        create_backup()