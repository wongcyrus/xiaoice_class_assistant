from google.cloud import firestore

def get_config():
    try:
        db = firestore.Client(database="xiaoice")
        doc_ref = db.collection('xiaoice_config').document('messages')
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            return get_default_config()
    except Exception:
        return get_default_config()

def get_default_config():
    return {
        "welcome_messages": {
            "en": "Welcome! How can I help you today?",
            "zh": "欢迎！今天我能为您做些什么？"
        },
        "goodbye_messages": {
            "en": "Goodbye! Have a great day!",
            "zh": "再见！祝您有美好的一天！"
        },
        "recommended_questions": {
            "en": [
                "What can you help me with?",
                "How does this work?",
                "Can you explain more about this topic?"
            ],
            "zh": [
                "你能帮我做什么？",
                "这是如何工作的？",
                "你能详细解释一下这个话题吗？"
            ]
        },
        "talk_responses": {
            "en": "I understand your question. Let me help you with that.",
            "zh": "我理解您的问题。让我来帮助您。"
        }
    }
