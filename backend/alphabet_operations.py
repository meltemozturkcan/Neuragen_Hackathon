import os
import base64
from flask import Flask, request, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from database.db_config import get_db_connection

# Proje kök dizinini al
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dosya yolları
AUDIO_FOLDER = os.path.join(BASE_DIR, 'audio_files')
IMAGE_FOLDER = os.path.join(BASE_DIR, 'images')

# Klasörleri oluştur
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

alphabet_bp = Blueprint('alphabet', __name__, url_prefix='/alphabet')

app = Flask(__name__)

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

# TEST REQUEST FOR THIS MODULE
@alphabet_bp.route('/test', methods=['GET'])
def test_api():
    conn = get_db_connection()
    print("conn: ", conn)
    conn.close()
    print(f"Test request successfully processed. :)")
    return create_response(
        status_code=200,
        success=True,
        message="Test isteği başarıyla alındı. :)",
        http_response="TEST_REQUEST_PROCESSED"
    )

# GET ALL AUDIO AND IMAGE DATA
@alphabet_bp.route('/getAllAudioAndImage', methods=['GET'])
def get_all_audio_and_image():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Tüm harf verilerini getir
        query_getAllLetters ="""SELECT id, letter, difficulty_level, category,  audio_path, image_path 
            FROM turkish_alphabet"""
        cur.execute(query_getAllLetters)
        turkishAlphabet = cur.fetchall()

        if turkishAlphabet is None:
            return create_response(
                status_code=404,
                success=False,
                message="Alfabe verisi mevcut değil.",
                http_response="TURKISH_ALPHABET_NOT_FOUND"
                )
        
        # Her kelime için ses ve görsel dosyalarını base64'e çevir
        formatted_audio_image_data = list()
        for letter in turkishAlphabet:
            # Dosya yollarını düzelt
            audio_path = get_file_path(letter['audio_path'], AUDIO_FOLDER)
            image_path = get_file_path(letter['image_path'], IMAGE_FOLDER)

            audioBase64_result = None
            imageBase64Result = None

            # Ses dosyasını base64'e çevir
            if audio_path:
                audioBase64_result = encode_file_to_base64(audio_path)

            # Görseli base64'e çevir
            if image_path:
                imageBase64Result = encode_file_to_base64(image_path)
        
            letter_data = {
                'id': letter['id'],
                'letter': letter['letter'],
                'difficulty_level': letter['difficulty_level'],
                'category': letter['category'],
                'audio_base64': audioBase64_result,
                'image_base64': imageBase64Result,
            }

            formatted_audio_image_data.append(letter_data) 

        return create_response(
            status_code=200,
            success=True,
            data=formatted_audio_image_data,
            message="Türkçe alfabesiyle ilişkili ses ve görüntü verisi başarıyla döndürüldü.",
            http_response="SUCCESSFULL"
        )    
    except Exception as e:
        return create_response(400, False, message=("ERROR: " + str(e)), http_response="ERROR_OCCURED")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def handle_alphabet_data_formatting(alphabet_data):
    # Her kelime için ses ve görsel dosyalarını base64'e çevir
    formatted_audio_image_data = list()
    hasThrownException = False
    exceptionResult = None
    for letter in alphabet_data:
        # Dosya yollarını düzelt
        audio_path = get_file_path(letter['audio_path'], AUDIO_FOLDER)
        image_path = get_file_path(letter['image_path'], IMAGE_FOLDER)

        print("AUDIO PATH: ", audio_path)
        print("AUDIO_DB_PATH: ", letter['audio_path'])
        print("IMAGE PATH: ", image_path)
        print("IMAGE_DB_PATH: ", letter['image_path'])

        audioBase64_result = None
        imageBase64Result = None

        # Ses dosyasını base64'e çevir
        if audio_path:
            audioBase64_result = encode_file_to_base64(audio_path)

        # Görseli base64'e çevir
        if image_path:
            imageBase64Result = encode_file_to_base64(image_path)

        print("au res:", audioBase64_result)
        print("im res:", imageBase64Result)
        
        exceptionResult = audioBase64_result if audioBase64_result.startswith("FAILURE: ") else imageBase64Result
        hasThrownException = hasThrownException or exceptionResult.startswith("FAILURE: ")

        if hasThrownException:
            return exceptionResult

        letter_data = {
            'id': letter['id'],
            'letter': letter['letter'],
            'difficulty_level': letter['difficulty_level'],
            'category': letter['category'],
            'audio_base64': audioBase64_result,
            'image_base64': imageBase64Result,
        }

        formatted_audio_image_data.append(letter_data)  
    return formatted_audio_image_data

def get_file_path(db_path, base_folder):
    """
    Veritabanındaki dosya yolunu tam dosya yoluna çevirir

    Args:
        db_path: Veritabanında kayıtlı dosya yolu
        base_folder: Ana klasör yolu
    Returns:
        str: Tam dosya yolu
    """
    if not db_path:
        return None

    # Dosya adını al
    filename = os.path.basename(db_path)
    # Tam yolu oluştur
    return os.path.join(base_folder, filename)


def encode_file_to_base64(file_path):
    """
    Dosyayı base64'e çevirir

    Args:
        file_path: Dosya yolu
    Returns:
        str: Base64 formatında dosya içeriği
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Dosya bulunamadı: {file_path}")
        message="FAILURE:Dosya bulunamadı " + file_path
        return message
    
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Dosya okuma hatası: {str(e)}")
        message="FAILURE:Dosya okuma hatası: " + str(e)
        return message





