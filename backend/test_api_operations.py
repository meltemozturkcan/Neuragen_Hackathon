from flask import Flask, request, jsonify, Blueprint

test_api__bp = Blueprint('test_api', __name__)
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

@test_api__bp.route('/', methods=['GET'])
def test_api():
    print(f"WELCOME! Test request successfully processed. :D")
    return create_response(
        status_code=200,
        success=True,
        message="Test isteği başarıyla alındı. :)",
        http_response="TEST_REQUEST_PROCESSED"
    )