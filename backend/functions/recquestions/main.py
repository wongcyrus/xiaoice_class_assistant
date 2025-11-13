import json
import uuid
import functions_framework
from auth_utils import validate_authentication
from firestore_utils import get_config

@functions_framework.http
def recquestions(request):
    # Authentication check
    auth_error = validate_authentication(request)
    if auth_error:
        return auth_error
    
    request_json = request.get_json(silent=True) or {}
    
    trace_id = request_json.get("traceId", str(uuid.uuid4()))
    language_code = request_json.get("languageCode", "en")
    
    config = get_config()
    recommended_questions = config.get("recommended_questions", {})
    
    response = {
        "data": recommended_questions.get(language_code, recommended_questions.get("en", [])),
        "traceId": trace_id
    }
    
    return json.dumps(response), 200, {"Content-Type": "application/json"}
