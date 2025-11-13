#!/usr/bin/env python3
"""
Test scripts for Xiaoice Class Assistant Cloud Functions
"""

import hashlib
import json
import os
import sys
import time
import uuid
import requests


def calculate_signature(body_string: str, secret_key: str, timestamp: str) -> str:
    """Calculate signature for authentication using v2 algorithm"""
    params = {"bodyString": body_string, "secretKey": secret_key, "timestamp": timestamp}
    signature_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hashlib.sha512(signature_string.encode("utf-8")).hexdigest().upper()


def test_talk_stream():
    """Test the /talk streaming endpoint"""
    print("Testing /talk streaming endpoint...")
    
    base_url = os.getenv("API_URL", "https://your-api-gateway-url")
    endpoint = "/talk"
    
    secret_key = os.getenv("XiaoiceChatSecretKey", "test_secret_key")
    access_key = os.getenv("XiaoiceChatAccessKey", "test_access_key")
    
    timestamp = str(int(time.time() * 1000))
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    payload = {
        "askText": "Hello, can you help me with the class?",
        "sessionId": session_id,
        "traceId": trace_id,
        "languageCode": "en",
        "extra": {}
    }
    
    body_string = json.dumps(payload, separators=(',', ':'))
    signature = calculate_signature(body_string, secret_key, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Sign": signature,
        "X-Key": access_key
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=body_string,
            headers=headers,
            stream=True,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"Received: {line}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_welcome():
    """Test the /welcome endpoint"""
    print("Testing /welcome endpoint...")
    
    base_url = os.getenv("API_URL", "https://your-api-gateway-url")
    endpoint = "/welcome"
    
    secret_key = os.getenv("XiaoiceChatSecretKey", "test_secret_key")
    access_key = os.getenv("XiaoiceChatAccessKey", "test_access_key")
    
    timestamp = str(int(time.time() * 1000))
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    payload = {
        "traceId": trace_id,
        "sessionId": session_id,
        "languageCode": "en"
    }
    
    body_string = json.dumps(payload, separators=(',', ':'))
    signature = calculate_signature(body_string, secret_key, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Sign": signature,
        "X-Key": access_key
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=body_string,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_goodbye():
    """Test the /goodbye endpoint"""
    print("Testing /goodbye endpoint...")
    
    base_url = os.getenv("API_URL", "https://your-api-gateway-url")
    endpoint = "/goodbye"
    
    secret_key = os.getenv("XiaoiceChatSecretKey", "test_secret_key")
    access_key = os.getenv("XiaoiceChatAccessKey", "test_access_key")
    
    timestamp = str(int(time.time() * 1000))
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    payload = {
        "traceId": trace_id,
        "sessionId": session_id,
        "languageCode": "en"
    }
    
    body_string = json.dumps(payload, separators=(',', ':'))
    signature = calculate_signature(body_string, secret_key, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Sign": signature,
        "X-Key": access_key
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=body_string,  # Use data instead of json
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_recquestions():
    """Test the /recquestions endpoint"""
    print("Testing /recquestions endpoint...")
    
    base_url = os.getenv("API_URL", "https://your-api-gateway-url")
    endpoint = "/recquestions"
    
    secret_key = os.getenv("XiaoiceChatSecretKey", "test_secret_key")
    access_key = os.getenv("XiaoiceChatAccessKey", "test_access_key")
    
    timestamp = str(int(time.time() * 1000))
    trace_id = str(uuid.uuid4())
    
    payload = {
        "traceId": trace_id,
        "languageCode": "en"
    }
    
    body_string = json.dumps(payload, separators=(',', ':'))
    signature = calculate_signature(body_string, secret_key, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Sign": signature,
        "X-Key": access_key
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=body_string,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


def test_config():
    """Test the /config endpoint"""
    print("Testing /config endpoint...")
    
    base_url = os.getenv("API_URL", "https://your-api-gateway-url")
    endpoint = "/config"
    
    secret_key = os.getenv("XiaoiceChatSecretKey", "test_secret_key")
    access_key = os.getenv("XiaoiceChatAccessKey", "test_access_key")
    
    timestamp = str(int(time.time() * 1000))
    
    payload = {
        "welcome_messages": {
            "en": "Hello! Welcome to our updated service!",
            "zh": "您好！欢迎使用我们更新的服务！"
        },
        "goodbye_messages": {
            "en": "Thank you for using our service! Goodbye!",
            "zh": "感谢您使用我们的服务！再见！"
        },
        "recommended_questions": {
            "en": [
                "How can I get started?",
                "What features are available?",
                "Can you help me with configuration?"
            ],
            "zh": [
                "我该如何开始？",
                "有哪些功能可用？",
                "您能帮我配置吗？"
            ]
        },
        "talk_responses": {
            "en": "I understand your question. Let me provide you with detailed assistance.",
            "zh": "我理解您的问题。让我为您提供详细的帮助。"
        }
    }
    
    body_string = json.dumps(payload, separators=(',', ':'))
    signature = calculate_signature(body_string, secret_key, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Sign": signature,
        "X-Key": access_key
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=body_string,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "talk":
            test_talk_stream()
        elif test_type == "welcome":
            test_welcome()
        elif test_type == "goodbye":
            test_goodbye()
        elif test_type == "recquestions":
            test_recquestions()
        elif test_type == "config":
            test_config()
        else:
            print("Usage: python test_functions.py [talk|welcome|goodbye|recquestions|config]")
    else:
        print("Running all function tests...")
        test_welcome()
        print("\n" + "="*50 + "\n")
        test_talk_stream()
        print("\n" + "="*50 + "\n")
        test_recquestions()
        print("\n" + "="*50 + "\n")
        test_goodbye()
        print("\n" + "="*50 + "\n")
        test_config()
