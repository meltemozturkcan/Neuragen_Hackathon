from flask import Flask, request, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime
from .db_config import get_db_connection


bp = Blueprint('users', __name__, url_prefix='/api')
app = Flask(__name__)

# Database bağlantı bilgileri
DB_CONFIG = {
    'dbname': 'neuragendev',
    'user': 'member1',
    'password': 'member1pass',
    'host': 'localhost',
    'port': '5432'
}
def getConn():
    conn = get_db_connection()
    return conn

def create_response(status_code, success, data=None, message=None, http_response=None):
    response = {
        'success': success,
        'data': data if data else {},
        'message': message if message else {},
        'statusCode': status_code,
        'http_response' : http_response
    }
    return jsonify(response), status_code

@bp.route('/test', methods=['GET'])
def test_api():
    print(f"Test request successfully processed. :)")
    return create_response(
        status_code=200,
        success=True,
        message="Test isteği başarıyla alındı. :)",
        http_response="TEST_REQUEST_PROCESSED"
    )


@bp.route('/signup', methods=['POST'])
def create_user():
    try:
        conn = getConn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        conn.autocommit = False

        data = request.get_json()
        required_fields = ['name', 'surname', 'birthYear', "schoolGrade", "email", "password", "confirmPassword"]

        # Zorunlu alanları kontrol et
        if not all(field in data for field in required_fields):
            return create_response(
                status_code=400,
                success=False,
                message= "Eksik Bilgi. Bu alanların girilmesi zorunludur: name, surname, birthYear, schoolGrade, email, şifre, tekrar şifre",
                http_response="INCOMPLETE_INFORMATION"
            )
        
        if data['password'] != data['confirmPassword']:
            return create_response(
                status_code=400,
                success=False,
                message="Şifreler uyuşmuyor. Tekrar deneyiniz lütfen.",
                http_response="PASSWORD_NOT_MATCHED_WITH_CONFIRMED_PASSWORD"
            )
        
        # Şifreyi hashle
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # Kullanıcıyı oluştur
        cur.execute("""
            INSERT INTO users (name, surname, birth_year, school_grade, email, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, surname, birth_year, school_grade, email, created_at, updated_at, is_active
        """, 
        (data['name'], data['surname'], data['birthYear'], data['schoolGrade'], data['email'], password_hash.decode('utf-8'),)
        )

        new_user = cur.fetchone()
        conn.commit()

        return create_response(
            status_code=201, 
            success=True, 
            data=new_user,
            message="Kaydınız başarıyla oluşturuldu.", 
            http_response="USER_CREATED")
    except psycopg2.IntegrityError as e:
        conn.rollback()  # UNIQUE constraint ihlali durumunda rollback yapılıyor  
        return create_response(
            status_code=409, 
            success=False,
            message="Bu email adresiyle önceden kayıt yapılmış.",
            http_response="EMAIL_CONFLICT")
    except Exception as e:
        conn.rollback()
        return create_response(400, False, message=("ERROR: " + str(e)), http_response="BAD_REQUEST")
    finally:
        # Bağlantı ve cursor'u her durumda kapatıyoruz
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@bp.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json() #type: dict

        if not data['email'] or not data['password']:
            return create_response(
                status_code=400,
                success=False,
                message="Lütfen zorunlu alanları giriniz: email and şifre.",
                http_response="EMAIL_OR_PASSWORD_NOT_EXIST")

        user = get_user_by_email(data['email']) # Type is ordered Dict

        if user:
            isActive = user.get('is_active')
            if not isActive:
                return create_response(
                    status_code=403, 
                    success=False, 
                    message="Bu hesap aktif değil.", 
                    http_response="FORBIDDEN_INACTIVE_ACCOUNT")
            
            isPassCorrect = check_password(data['password'], user.get('password_hash'))
            if isPassCorrect:
                # Password is correct, proceed with login
                print("user dict: ", user)
                user.pop('password_hash', None)
                print("user dict after deleted pass:", user)
                return create_response(
                    status_code=200,
                    success=True,
                    data={"User":user},
                    message="Kullanıcı girişi başarılı.",
                    http_response="LOGIN_SUCCESSFULL")
            if not isPassCorrect:
                # Password is incorrect
                return create_response(
                    status_code=400,
                    success=False,
                    message="Geçersiz parola.",
                    http_response="LOGIN_UNSUCCESSFULL")
        else:
            # User not found
            return create_response(
                    status_code=404,
                    success=False,
                    message="Bu email adresi ile kayıtlı bir kullanıcı bulunmamaktadır.",
                    http_response="USER_NOT_FOUND")

        user.pop('password_hash')  # Şifre hash'ini response'dan çıkar
        responseObject={'id':user[0], 'email':user[1], 'is_active':user[3]} 
        return create_response(
            200,
            True,
            data=responseObject,
            message="Giriş işlemi başarılı.",
            http_response="SUCCESS_LOGIN"
        )
    except Exception as e:
        return create_response(400, False, message="ERROR: " + str(e), http_response="BAD_REQUEST")


@bp.route('/get/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Kullanıcı bilgilerini ve istatistiklerini getir
        query_getUserById = """
            SELECT id, name, surname, birth_year, school_grade, email, is_active
            FROM users
            WHERE id = %s;
        """
        cur.execute(query_getUserById, (user_id,))
        user = cur.fetchone()
        if not user:
            return create_response(
                status_code=404, 
                success=False, 
                message="Kullanıcı bulunamadı.",
                http_response="USER_NOT_FOUND")

        return create_response(
            status_code=200,
            success=True,
            data={'User': user},
            message="Kullanıcı bilgileri başarıyla döndürüldü.",
            http_response="SUCCESS"
        )
    except Exception as e:
        return create_response(500, False, message=("ERROR: " + str(e)), http_response="ERROR_OCCURED")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()

        if not data:
            return create_response(
                400,
                False,
                message="Güncellenecek veri bulunamadı"
            )

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        update_fields = []
        params = []

        # Güncellenebilir alanlar
        if 'username' in data:
            update_fields.append("username = %s")
            params.append(data['username'])
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        if 'is_active' in data:
            update_fields.append("is_active = %s")
            params.append(data['is_active'])

        if not update_fields:
            return create_response(
                400,
                False,
                message="Güncellenecek alan bulunamadı"
            )

        params.append(user_id)
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, username, email, created_at, is_active
        """

        cur.execute(query, params)
        updated_user = cur.fetchone()

        if not updated_user:
            return create_response(404, False, message="Kullanıcı bulunamadı")

        conn.commit()
        cur.close()
        conn.close()

        return create_response(
            200,
            True,
            data={'user': updated_user},
            message="Kullanıcı başarıyla güncellendi"
        )

    except psycopg2.IntegrityError:
        return create_response(
            409,
            False,
            message="Bu email veya kullanıcı adı zaten kullanımda"
        )
    except Exception as e:
        return create_response(500, False, message=("ERROR: " + str(e)), http_response="ERROR_OCCURED")


@bp.route('/api/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Kullanıcı istatistiklerini getir
        cur.execute("""
            SELECT us.*, 
                   COUNT(tr.id) as total_tests_taken,
                   AVG(tr.pronunciation_score) as overall_average,
                   MAX(tr.pronunciation_score) as highest_score,
                   MIN(tr.pronunciation_score) as lowest_score
            FROM user_stats us
            LEFT JOIN test_results tr ON us.user_id = tr.user_id
            WHERE us.user_id = %s
            GROUP BY us.id
        """, (user_id,))

        stats = cur.fetchone()

        if not stats:
            return create_response(404, False, message="Kullanıcı istatistikleri bulunamadı")

        # Kategori bazlı ortalama skorları getir
        cur.execute("""
            SELECT tw.category, 
                   AVG(tr.pronunciation_score) as category_average,
                   COUNT(tr.id) as tests_in_category
            FROM test_results tr
            JOIN test_words tw ON tr.word_tested = tw.word
            WHERE tr.user_id = %s
            GROUP BY tw.category
        """, (user_id,))

        category_stats = cur.fetchall()
        stats['category_statistics'] = category_stats

        cur.close()
        conn.close()

        return create_response(
            200,
            True,
            data={'stats': stats}
        )

    except Exception as e:
        return create_response(500, False, message=("ERROR: " + str(e)), http_response="ERROR_OCCURED")

def get_user_by_email(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query_getUserByEmail = """SELECT * 
                                    FROM users 
                                    WHERE email = %s"""
        cur.execute(query_getUserByEmail, (email,))
        user_data = cur.fetchone()
        return user_data
    except Exception as e:
        message="ERROR: " + str(e)
        return create_response(400, False, message=message, http_response="ERROR_OCCURED")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

if __name__ == '__main__':
    app.run(debug=True)