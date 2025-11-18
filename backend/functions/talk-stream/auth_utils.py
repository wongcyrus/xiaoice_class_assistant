import hashlib
import json
import os


def validate_authentication(request):
    """Validates authentication headers and returns error response if invalid."""
    try:
        timestamp = request.headers.get("X-Timestamp") or request.headers.get("timestamp")
        signature = request.headers.get("X-Sign") or request.headers.get("signature")
        access_key = request.headers.get("X-Key") or request.headers.get("key")

        stored_secret_key = os.getenv("XIAOICE_CHAT_SECRET_KEY")
        valid_access_key = os.getenv("XIAOICE_CHAT_ACCESS_KEY")

        if not all([stored_secret_key, valid_access_key]):
            return json.dumps({"error": "Server configuration error"}), 500

        if not all([timestamp, signature, access_key]):
            return json.dumps({"error": "Missing authentication headers"}), 401

        if access_key != valid_access_key:
            return json.dumps({"error": "Invalid access key"}), 401

        body_string = request.data.decode("utf-8")
        
        # Calculate v2 signature
        params = {"bodyString": body_string, "secretKey": stored_secret_key, "timestamp": timestamp}
        signature_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        calculated_signature = hashlib.sha512(signature_string.encode("utf-8")).hexdigest().upper()

        if calculated_signature != signature:
            return json.dumps({"error": "Invalid signature"}), 401

        return None

    except Exception as e:
        return json.dumps({"error": f"Authentication failed: {e}"}), 401
