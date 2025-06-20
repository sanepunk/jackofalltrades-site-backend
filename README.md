# jackofalltrades Download Stats API

FastAPI backend for fetching download statistics from Pepy.tech API, solving CORS issues for the frontend.

## 🚀 Features

- **CORS Enabled**: Allows frontend to make requests without CORS issues
- **Secure API Key Handling**: Environment-based API key configuration
- **Error Handling**: Comprehensive error responses and status codes
- **Rate Limiting**: Respects Pepy.tech API rate limits
- **Auto Documentation**: Interactive API docs with Swagger UI
- **Health Checks**: Built-in health monitoring endpoints

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Pepy.tech API key

## 🛠️ Installation

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Pepy.tech API key:
```env
PEPPY_API_KEY=your_actual_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173
```

## 🎯 Usage

### Start the server
```bash
# Method 1: Using the startup script
python start.py

# Method 2: Direct uvicorn command
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Using the main.py
python main.py
```

The server will start at `http://localhost:8000`

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic health check |
| `/health` | GET | Detailed health check with API key status |
| `/api/downloads` | GET | Raw download statistics |
| `/api/downloads/formatted` | GET | Formatted download statistics |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation |

### Example Response

```json
{
  "success": true,
  "total_downloads": 1523456,
  "project_id": "jackofalltrades",
  "versions": ["0.1.0", "0.1.1", "0.2.0"],
  "last_updated": "2024-01-01T12:00:00Z",
  "error": null
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PEPPY_API_KEY` | None | **Required** - Your Pepy.tech API key |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `True` | Enable debug mode and auto-reload |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS |

### Getting Your API Key

1. Visit [pepy.tech](https://pepy.tech/)
2. Sign up or log in to your account
3. Go to your user profile
4. Copy your API key
5. Add it to your `.env` file

## 🌐 Frontend Integration

Update your frontend to use the backend API instead of direct Pepy.tech calls:

```javascript
// Replace the Pepy.tech API call with:
const response = await fetch('http://localhost:8000/api/downloads');
const data = await response.json();
```

## 🔍 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Download Stats
```bash
curl http://localhost:8000/api/downloads
```

### API Documentation
Visit `http://localhost:8000/docs` in your browser for interactive API documentation.

## 🚨 Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "total_downloads": 0,
  "project_id": "jackofalltrades",
  "versions": [],
  "last_updated": ""
}
```

### Common Error Codes

- `401`: Invalid API key
- `404`: Package not found
- `429`: Rate limit exceeded
- `500`: Server configuration error
- `503`: Pepy.tech API unavailable

## 📊 Rate Limiting

- **Free users**: 10 requests per minute
- **Pro users**: 100 requests per minute

The backend respects these limits and provides appropriate error messages when exceeded.

## 🔒 Security

- API key is stored securely in environment variables
- CORS is configured to only allow specific origins
- No sensitive data is logged
- Input validation and sanitization

## 🐛 Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in `.env`
- Verify the key is valid on pepy.tech
- Check that the key has the necessary permissions

### CORS Issues
- Ensure `FRONTEND_URL` matches your frontend URL
- Check that the frontend is making requests to the correct backend URL

### Connection Issues
- Verify the backend is running on the expected port
- Check firewall settings
- Ensure Python dependencies are installed

## 📝 Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── start.py             # Startup script
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── .env                # Environment variables (create this)
└── README.md           # This file
```

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Add your changes to `main.py`
4. Test thoroughly
5. Update documentation
6. Submit a pull request

## 📞 Support

- 🐛 **Issues**: Report bugs or request features
- 📧 **Email**: Technical support
- 📖 **Docs**: API documentation at `/docs`

---

Made with ❤️ for the jackofalltrades community 