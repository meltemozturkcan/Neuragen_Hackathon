import os
import base64
from flask import Flask, request, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from database.db_config import get_db_connection
from config import Config
from werkzeug.utils import secure_filename
import google.generativeai as genai
import json
import ast


upload_folder = Config.UPLOAD_FOLDER
os.makedirs(upload_folder, exist_ok=True)
genai.configure(api_key=Config.GEMINI_API_KEY)

# Dosya yolları
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_FOLDER = os.path.join(BASE_DIR, 'audio_files')

gemini_response_bp = Blueprint('gemini', __name__, url_prefix='/gemini')

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
@gemini_response_bp.route('/create-prompt', methods=['POST'])
def insert_prompt():
    try:
        conn = getConn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        model_name= Config.GEMINI_MODEL
        prompt = prepare_prompt("REFERENCE_AUDIO_URI", "REFERENCE_AUDIO_PATH", "TEST_AUDIO_URI", "TEST_AUDIO_PATH", "LETTER")
        cur.execute("""
            INSERT INTO prompt (prompt, model_name)
            VALUES (%s, %s)
            RETURNING id, prompt, model_name, created_at
        """, 
        (prompt, model_name,)
        )

        new_prompt = cur.fetchone()
        conn.commit()

        return create_response(
            status_code=201, 
            success=True, 
            data=new_prompt,
            message="Prompt veritabanına kaydedildi.", 
            http_response="USER_CREATED")
    except Exception as e:
        conn.rollback()
        return create_response(400, False, message=("ERROR: " + str(e)), http_response="BAD_REQUEST")
    finally:
        # Bağlantı ve cursor'u her durumda kapatıyoruz
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@gemini_response_bp.route('/submit-test', methods=['POST'])
def get_gemini_response():
    try:
        conn = getConn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        data = request.get_json()

        if not data['userId'] or not data['letterId'] or not data['userVoiceRecord']:
            return create_response(
                status_code=400,
                success=False,
                message="Lütfen zorunlu alanları giriniz: userId, letterId ve userVoiceRecord.",
                http_response="REQUIRED_FIELD_NOT_EXIST")

        # Kullanıcı kontrolü
        query_getUserById = """SELECT id, name, surname, birth_year, school_grade, email, is_active
            FROM users
            WHERE id = %s;
        """
        cur.execute(query_getUserById, (data['userId'],))
        user = cur.fetchone()
        if not user:
            return create_response(
                status_code=404, 
                success=False, 
                message="Kullanıcı bulunamadı.",
                http_response="USER_NOT_FOUND")

        # Letter data kontrolü
        query_getLetterById ="""SELECT id, letter, difficulty_level, category,  audio_path 
            FROM turkish_alphabet WHERE id = %s"""
        cur.execute(query_getLetterById,(data['letterId'],))
        letterFromDB = cur.fetchone()

        if letterFromDB is None:
            return create_response(
                status_code=404,
                success=False,
                message="İlgili harf veritabanında bulunamadı.",
                http_response="LETTER_NOT_FOUND")

        conn.commit()

        # User Ses kaydı çevirme
        # Base64'ü decode et
        audio_bytes = base64.b64decode(data['userVoiceRecord'])

        # Geçici dosya yolu oluştur
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'audio_{timestamp}.wav'
        userVoiceRecord_filepath = os.path.join(upload_folder, secure_filename(filename))

        # Ses verisini kontrol et ve kaydet
        with open(userVoiceRecord_filepath, 'wb') as f:
            f.write(audio_bytes)
        
        
        # Reference ses kaydını al
        ref_letter = letterFromDB['letter']
        ref_audio_path = get_file_path(letterFromDB['audio_path'], AUDIO_FOLDER)

        #Ses dosyasını Gemini için hazırla
        # Upload the file using the function
        uploaded_referenceVoice = upload_to_gemini(ref_audio_path, mime_type="audio/wav")
        uploaded_userVoiceRecord = upload_to_gemini(userVoiceRecord_filepath, mime_type="audio/wav")

        #Gemini configurations
        generationConfig = Config.GENERATION_CONFIG
        model = genai.GenerativeModel(model_name=Config.GEMINI_MODEL, generation_config=generationConfig,)
        files_toBeUpload = [uploaded_referenceVoice, uploaded_userVoiceRecord,]

        # Prompt hazırla ve analiz yap
        prompt = prepare_prompt(uploaded_referenceVoice, letterFromDB['audio_path'], uploaded_userVoiceRecord, filename, ref_letter)
        
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [files_toBeUpload[0], files_toBeUpload[1]]}])
        
        response = chat_session.send_message(prompt)
        print("RESPONSE: ", response)

        # JSON parse
        analysis = response.text
        print("ANALYSIS: ", analysis)
        resulted_gemini_response = parse_response_as_JSON(analysis)
        if type(resulted_gemini_response) == type(-1):
            errorMsg ="JSON okuma hatası, Eksik veri hatası ya da Beklenmeyen hata"
            return create_response(400, False, message=("ERROR: " + errorMsg), http_response="BAD_REQUEST")
        
        if type(resulted_gemini_response) == type(-5):
            errorMsg ="Gemini şu anda hizmwt veremiyor."
            return create_response(400, False, message=("ERROR: " + errorMsg), http_response="BAD_REQUEST")
        
        for elem in resulted_gemini_response:
            print("elem: ", elem, " type: ", type(elem))
        response_data = get_gemini_response_dict(resulted_gemini_response)
        detailed_feedback_resp = response_data['detailed_feedback']

        print("---- detailed:" , detailed_feedback_resp)

        cur.execute("""
            INSERT INTO gemini_response (pronunciation_score, areas_of_improvement, vowel, consonant, clarity, confidence_score, prompt, model_name )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, pronunciation_score, areas_of_improvement, consonant, clarity, confidence_score, prompt, model_name, created_at
        """, 
        (response_data["pronunciation_score"], response_data["areas_of_improvement"], 
         detailed_feedback_resp['vowel'], detailed_feedback_resp['Consonant'],
         detailed_feedback_resp['Clarity'], response_data['confidence_score'], prompt, Config.GEMINI_MODEL)
        )

        savedGeminiResponse = cur.fetchone()
        conn.commit()

        cur.execute("""
            INSERT INTO test_results (user_id, letter_id, gemini_response_id)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, letter_id, gemini_response_id, created_at 
            """, (data['userId'], data['letterId'], savedGeminiResponse['id'],))
        savedTestResult = cur.fetchone()
        conn.commit()
        print("saved Test result: ", savedTestResult)
    
        return create_response(
            status_code=200,
            success=True,
            message="Test isteği başarıyla alındı. :)",
            data={'userID': user['id'], 'gemini_response':savedGeminiResponse},
            http_response="SUCCESS"
        )

    except Exception as e:
        conn.rollback()
        return create_response(400, False, message=("ERROR: " + str(e)), http_response="BAD_REQUEST")
    finally:
        # Bağlantı ve cursor'u her durumda kapatıyoruz
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def get_file_path(db_path, base_folder):
    if not db_path:
        return None
    
    filename = os.path.basename(db_path)
    return os.path.join(base_folder, filename)

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def prepare_prompt(reference_uri, reference_path, test_uri, test_path, letter):
        print("REF URI: ", reference_uri)
        print("TEST URI: ", test_uri)

        prompt = f"""
        Analyze and compare these two audio pronunciations for the letter "{letter}".
        Original pronunciation file: {reference_path}
        Test pronunciation file: {test_path}
        Please provide a detailed analysis including:
        1. Pronunciation accuracy score (0-100)
        2. Specific areas requiring improvement
        3. Detailed feedback about:
           - Vowel sounds
           - Consonant sounds
           - Overall clarity
        4. Confidence score of this analysis (0-100)
        Format the response as a JSON object like below, translate value part in the response in Turkish language:
        {{
            "pronunciation_score": Float,
            "areas_of_improvement": String,
            "detailed_feedback": {{
                "vowel": String,
                "Consonant": String,
                "Clarity": String
            }},
            "confidence_score": Float
        }}
        """
        return prompt
    
def parse_response_as_JSON(geminiResponse):
    try:
        if not ("pronunciation" in (geminiResponse)):
            return -5
        else:
            print("The string contain 'pronunciation'.")
        # String içindeki JSON kısmını al
        start_index = geminiResponse.find('{')
        end_index = geminiResponse.rfind('}') + 1
        json_str = geminiResponse[start_index:end_index]
        # JSON'ı parse et
        parsedData = json.loads(json_str)
        return parsedData

    except json.JSONDecodeError as e:
        print(f"\n JSON okuma hatası: {str(e)}")
        return -1
    except KeyError as e:
        print(f"\n Eksik veri hatası: {str(e)}")
        return -1
    except Exception as e:
        print(f"\n Beklenmeyen hata: {str(e)}")
        return -1

def get_gemini_response_dict(gemini_response):
    pronunciation_score = gemini_response["pronunciation_score"] if gemini_response["pronunciation_score"] else float(-1)
    areas_of_improvement = gemini_response["areas_of_improvement"] if gemini_response["areas_of_improvement"] else "empty"
    detailed_feedback = gemini_response["detailed_feedback"] if gemini_response["detailed_feedback"] else "empty"
    vowel = None
    consonant = None
    clarity = None
    if detailed_feedback:
        vowel = detailed_feedback["vowel"] if detailed_feedback["vowel"] else "empty"
        consonant = detailed_feedback["Consonant"] if detailed_feedback["Consonant"] else "empty"
        clarity = detailed_feedback["Clarity"] if detailed_feedback["Clarity"] else "empty"
    
    confidence_score = gemini_response["confidence_score"] if gemini_response["confidence_score"] else float(-1)

    responseData = {"pronunciation_score":pronunciation_score,
                    "areas_of_improvement":areas_of_improvement,
                    "detailed_feedback":detailed_feedback,
                    "confidence_score":confidence_score}
    
    return responseData



