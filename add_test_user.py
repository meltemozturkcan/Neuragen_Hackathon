from database.user_operations import UserOperations

# Veritabanı bağlantı ayarları - POSTGRES ŞİFRENİZİ DOĞRU GİRİN
db_config = {
    'dbname': 'neuragendev',
    'user': 'postgres',
    'password': '1234',  # PostgreSQL kurulumunda belirlediğiniz şifre
    'host': 'localhost',
    'port': '5432'
}


def add_test_users():
    try:
        user_ops = UserOperations(db_config)

        # Tek bir test kullanıcısı ekleyelim
        user_id = user_ops.add_user(
            username="test_user1",
            email="test1@example.com",
            password="123456"  # Basit bir şifre kullanalım
        )

        if user_id:
            print(f"Kullanıcı başarıyla eklendi. ID: {user_id}")
        else:
            print("Kullanıcı eklenemedi!")

    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")


if __name__ == "__main__":
    add_test_users()