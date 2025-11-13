import json
import functions_framework
from google.cloud import firestore
from auth_utils import validate_authentication

@functions_framework.http
def config(request):
    auth_error = validate_authentication(request)
    if auth_error:
        return auth_error
    
    if request.method != 'POST':
        return json.dumps({"error": "Method not allowed"}), 405, {"Content-Type": "application/json"}
    
    request_json = request.get_json(silent=True)
    if not request_json:
        return json.dumps({"error": "Invalid JSON"}), 400, {"Content-Type": "application/json"}
    
    try:
        db = firestore.Client(database="xiaoice")
        config_data = {
            "welcome_messages": request_json.get("welcome_messages", {}),
            "goodbye_messages": request_json.get("goodbye_messages", {}),
            "recommended_questions": request_json.get("recommended_questions", {}),
            "talk_responses": request_json.get("talk_responses", {}),
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('xiaoice_config').document('messages')
        doc_ref.set(config_data)
        
        return json.dumps({"success": True}), 200, {"Content-Type": "application/json"}
        
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}
