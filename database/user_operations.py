from flask import Flask, request, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime
bp = Blueprint('users', __name__, url_prefix='/api')
app = Flask(__name__)

# Database bağlantı bilgileri
DB_CONFIG = {
    'dbname': 'neuragendev',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_response(status_code, success, data=None, message=None):
    response = {
        'success': success,
        'data': data if data else {},
        'message': message
    }
    return jsonify(response), status_code

@bp.route('/test', methods=['GET'])
def test_api():
    print(f"Test user created with ID: ")
    return create_response(
        200,
        True,
        message="Eksik bilgi. Username, email ve password zorunludur."
    )
@bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        required_fields = ['username', 'email', 'password']

        # Zorunlu alanları kontrol et
        if not all(field in data for field in required_fields):
            return create_response(
                400,
                False,
                message="Eksik bilgi. Username, email ve password zorunludur."
            )

        # Şifreyi hashle
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Kullanıcıyı oluştur
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email, created_at, is_active
        """, (data['username'], data['email'], password_hash.decode('utf-8')))

        new_user = cur.fetchone()

        # Kullanıcı istatistikleri tablosunu oluştur
        cur.execute("""
            INSERT INTO user_stats (user_id)
            VALUES (%s)
        """, (new_user['id'],))

        conn.commit()
        cur.close()
        conn.close()

        return create_response(
            201,
            True,
            data={'user': new_user},
            message="Kullanıcı başarıyla oluşturuldu"
        )

    except psycopg2.IntegrityError as e:
        return create_response(
            409,
            False,
            message="Bu email veya kullanıcı adı zaten kullanımda"
        )
    except Exception as e:
        return create_response(500, False, message=str(e))


@app.route('/api/users/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return create_response(
                400,
                False,
                message="Email ve şifre gereklidir"
            )

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Kullanıcıyı bul
        cur.execute("""
            SELECT id, username, email, password_hash, is_active
            FROM users
            WHERE email = %s
        """, (data['email'],))

        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return create_response(404, False, message="Kullanıcı bulunamadı")

        if not user['is_active']:
            return create_response(403, False, message="Hesap aktif değil")

        # Şifre kontrolü
        if not bcrypt.checkpw(data['password'].encode('utf-8'),
                              user['password_hash'].encode('utf-8')):
            return create_response(401, False, message="Hatalı şifre")

        user.pop('password_hash')  # Şifre hash'ini response'dan çıkar
        return create_response(
            200,
            True,
            data={'user': user},
            message="Giriş başarılı"
        )

    except Exception as e:
        return create_response(500, False, message=str(e))


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Kullanıcı bilgilerini ve istatistiklerini getir
        cur.execute("""
            SELECT id, username, email, created_at, is_active
            FROM users
            WHERE id = %s;
        """, (user_id,))

        user = cur.fetchone()

        if not user:
            return create_response(404, False, message="Kullanıcı bulunamadı")


        cur.close()
        conn.close()

        return create_response(
            200,
            True,
            data={'user': user}
        )

    except Exception as e:
        return create_response(500, False, message=str(e))


@app.route('/api/users/<int:user_id>', methods=['PUT'])
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
        return create_response(500, False, message=str(e))


@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
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
        return create_response(500, False, message=str(e))


if __name__ == '__main__':
    app.run(debug=True)