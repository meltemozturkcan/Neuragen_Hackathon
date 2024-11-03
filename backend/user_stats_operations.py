from flask import Flask, request, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime
from database.db_config import get_db_connection

user_stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

app = Flask(__name__)

def create_response(status_code, success, data=None, message=None, http_response=None):
    response = {
        'success': success,
        'data': data if data else {},
        'message': message if message else {},
        'statusCode': status_code,
        'http_response' : http_response
    }
    return jsonify(response), status_code

@user_stats_bp.route('/get/<int:user_id>', methods=['POST'])
def calculate_user_statsd(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        SQLQuery = """
        INSERT INTO user_stats (user_id, total_tests, average_pronunciation_score, avg_clarity, last_test_date, created_at)
        SELECT u.id AS user_id,
        COUNT(tr.id) AS total_tests,
        AVG(gr.pronunciation_score) AS average_pronunciation_score,
        AVG(gr.clarity) AS avg_clarity,
        MAX(tr.created_at) AS last_test_date,
        NOW() AS created_at FROM users u 
        JOIN test_results tr ON u.id = tr.user_id
        JOIN gemini_response gr ON tr.gemini_response_id = gr.id 
        GROUP BY u.id;
        """

        # Execute the query
        cur.execute(SQLQuery, (user_id,))
        user_stats = cur.fetchall()
        print("---- user_stats ----")
        print(user_stats)

        if user_stats:
            return create_response(status_code=200, success=True, data={"statistics":user_stats}, 
                            message="Kullanıcı test istatistikleri başarıyla döndürüldü.",
                            http_response="SUCCESS")
        
        return create_response(
            status_code=404, success=False, 
            message="Kullanıcıya ait istatistik verisi bulunmamaktadır.", 
            http_response="NOT_FOUND")
    
    except Exception as e:
        conn.rollback()
        return create_response(400, False, message=("ERROR: " + str(e)), http_response="BAD_REQUEST")
    finally:
        # Bağlantı ve cursor'u her durumda kapatıyoruz
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


        
