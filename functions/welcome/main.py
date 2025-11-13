import json
import uuid
from datetime import datetime
import functions_framework
from auth_utils import validate_authentication
from firestore_utils import get_config

@functions_framework.http
def welcome(request):
    auth_error = validate_authentication(request)
    if auth_error:
        return auth_error
    
    request_json = request.get_json(silent=True) or {}
    
    trace_id = request_json.get("traceId", str(uuid.uuid4()))
    session_id = request_json.get("sessionId", str(uuid.uuid4()))
    language_code = request_json.get("languageCode", "en")
    
    config = get_config()
    welcome_messages = config.get("welcome_messages", {})
    
    response = {
        "id": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "traceId": trace_id,
        "sessionId": session_id,
        "replyText": welcome_messages.get(language_code, welcome_messages.get("en", "Welcome!")),
        "replyType": "Welcome",
        "timestamp": datetime.now().timestamp(),
        "extra": request_json.get("extra", {})
    }
    
    return json.dumps(response), 200, {"Content-Type": "application/json"}
