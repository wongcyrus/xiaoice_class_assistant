# Xiaoice Class Assistant

A comprehensive solution for integrating Xiaoice digital human interactions with classroom assistance, consisting of a serverless backend API and a desktop client for screen monitoring.

## 📋 Project Overview

This project implements the [Xiaoice Digital Human Dialogue Service Interface Protocol](https://aibeings-vip.xiaoice.com/) to enable intelligent classroom assistance through digital avatars. The system provides:

- **Backend API**: Serverless GCP Cloud Functions handling chat, welcome/goodbye messages, and question recommendations
- **Client Application**: Cross-platform desktop app for screen capture and OCR-based content monitoring

## 🏗️ Architecture

```
xiaoice_class_assistant/
├── backend/              # Serverless API infrastructure
│   ├── functions/        # Cloud Function endpoints
│   ├── cdktf/           # Infrastructure as Code (CDKTF)
│   ├── admin_tools/     # API key management tools
│   └── tests/           # Unit tests
└── client/              # Desktop monitoring application
    ├── monitor/         # Core monitoring modules
    └── window_monitor.py
```

## 🚀 Quick Start

### Prerequisites

- **GCP Account** with billing enabled
- **Node.js** 18+ (for CDKTF deployment)
- **Python** 3.8+ (for functions and client)
- **Terraform** (installed via CDKTF)
- **gcloud CLI** configured

### 1. Backend Setup & Deployment

#### Step 1: Authenticate with GCP

```bash
# Login to GCP
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project <your-project-id>
gcloud auth application-default set-quota-project <your-project-id>
```

#### Step 2: Configure Environment

Create `.env` file in `backend/cdktf/`:

```bash
cd backend/cdktf
cp .env.template .env
```

Edit `.env` with your values:

```bash
PREFIX=your-prefix
PROJECTID=your-gcp-project-id
BILLING_ACCOUNT=XXXXXX-XXXXXX-XXXXXX
REGION=us-east1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
XIAOICE_CHAT_SECRET_KEY=your-generated-secret-key
XIAOICE_CHAT_ACCESS_KEY=your-generated-access-key
```

**Generate Authentication Keys:**
```bash
# Generate SecretKey (for signing)
openssl rand -hex 32

# Generate AccessKey (for identification)
openssl rand -hex 32
```

#### Step 3: Deploy Infrastructure

```bash
cd backend
./deploy.sh
```

This script will:
1. Install CDKTF CLI and dependencies
2. Generate provider bindings
3. Deploy all Cloud Functions and API Gateway
4. Output API endpoint URLs

**Manual deployment:**
```bash
cd backend/cdktf
npm install
npm install cdktf-cli@latest
npx cdktf get
npx cdktf deploy --auto-approve
```

#### Step 4: Note Your API Endpoint

After deployment, save the API Gateway URL from the output:
```
api_gateway_url = https://your-gateway-xxxxxx.apigateway.your-project.cloud.goog
```

### 2. API Key Management (Optional)

Manage API keys for Xiaoice platform integration:

```bash
cd backend/admin_tools
./setup.sh
source venv/bin/activate

# Create API key
python create_api_key.py

# Delete API key
python delete_api_key.py <key-id>
```

Configuration is stored in `api_key.json`.

### 3. Client Setup

#### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

#### Install Client

```bash
cd client
pip install -e .
```

#### Run Client

```bash
window-monitor
```

The client will:
- Capture screenshots every second
- Perform OCR to extract text
- Save images when text content changes
- Store captures in `~/window_monitor_captures/`

## 📡 API Endpoints

All endpoints require authentication headers:

```
X-Timestamp: <current-timestamp-milliseconds>
X-Sign: <SHA512-signature>
X-Key: <access-key>
```

### Signature Calculation

```python
import hashlib
import json

# Parameters
params = {
    "bodyString": json.dumps(request_body),
    "secretKey": "your-secret-key",
    "timestamp": "1234567890123"
}

# Generate signature
signature_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
signature = hashlib.sha512(signature_string.encode("utf-8")).hexdigest().upper()
```

### Available Endpoints

#### 1. POST `/api/talk` - Streaming Chat
SSE (Server-Sent Events) streaming response.

**Request:**
```json
{
  "askText": "Hello, how are you?",
  "sessionId": "uuid",
  "traceId": "uuid",
  "languageCode": "en",
  "deviceId": "device-123",
  "userParams": "custom-params",
  "langByAsr": "en",
  "extra": {}
}
```

**Response:** Stream of JSON objects with `replyText`, `isFinal`, etc.

#### 2. POST `/api/welcome` - Welcome Message
Returns initial greeting message.

#### 3. POST `/api/goodbye` - Goodbye Message
Returns farewell message.

#### 4. POST `/api/recquestions` - Recommended Questions
Returns list of suggested questions.

**Response:**
```json
{
  "data": ["Question 1?", "Question 2?", "Question 3?"],
  "traceId": "uuid"
}
```

## 🧪 Testing

```bash
cd backend/tests
./run_tests.sh
```

Or run specific tests:
```bash
pytest test_functions.py -v
pytest test_functions.py::test_talk_stream_endpoint -v
```

## 🔐 Security & Configuration

### Environment Variables

The backend requires these environment variables (set in deployment):

- `XIAOICE_CHAT_SECRET_KEY` - Secret key for signature verification
- `XIAOICE_CHAT_ACCESS_KEY` - Access key for client identification
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_CLOUD_LOCATION` - Resource location
- `GOOGLE_GENAI_USE_VERTEXAI` - Enable Vertex AI integration

### Xiaoice Platform Configuration

In the Xiaoice Employee Platform (员工平台):

1. Navigate to Settings → Partner Integration
2. Set API endpoint to your API Gateway URL
3. Configure authentication:
   - **AccessKey (X-Key):** Your `XIAOICE_CHAT_ACCESS_KEY`
   - **SecretKey:** Your `XIAOICE_CHAT_SECRET_KEY`

## 🛠️ Development

### Project Structure

**Backend Functions:**
- `talk-stream/` - Main chat with Gemini AI integration (2GB memory, 20min timeout)
- `welcome/` - Welcome message endpoint
- `goodbye/` - Goodbye message endpoint  
- `recquestions/` - Recommended questions endpoint
- `config/` - Configuration endpoint

**CDKTF Components:**
- `api-gateway-construct.ts` - API Gateway with OpenAPI spec
- `cloud-function-construct.ts` - Individual function deployment
- `cloud-function-deployment-construct.ts` - Shared deployment resources
- `firestore-construct.ts` - Firestore database setup

### Local Development

1. Set environment variables
2. Run functions locally:
```bash
cd backend/functions/talk-stream
pip install -r requirements.txt
functions-framework --target=talk_stream --debug
```

### Update Deployment

```bash
cd backend
./deploy.sh
```

Or update specific function:
```bash
cd backend/cdktf
npx cdktf deploy --auto-approve
```

## 📚 Documentation

- [Xiaoice API Protocol Documentation](https://aibeings-vip.xiaoice.com/) (Chinese)
- [Backend README](backend/README.md)
- [Client README](client/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is part of a classroom assistant system for educational purposes.

## 🐛 Troubleshooting

### "Invalid signature" Error
- Verify `XIAOICE_CHAT_SECRET_KEY` and `XIAOICE_CHAT_ACCESS_KEY` match between client and server
- Check timestamp is current (within 5 minutes)
- Ensure signature calculation matches the protocol exactly

### Deployment Fails
- Verify GCP billing is enabled
- Check IAM permissions for Cloud Functions and API Gateway
- Ensure `.env` file has all required variables

### Client Not Capturing
- Verify Tesseract OCR is installed: `tesseract --version`
- Check permissions for screen capture on macOS/Windows
- Review logs in `~/window_monitor_captures/`

## 📞 Support

For issues related to:
- **Xiaoice Platform:** Contact Xiaoice support
- **Backend/Infrastructure:** Open an issue in this repository
- **Client Application:** Check client README or open an issue
