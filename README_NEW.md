# jackofalltrades Backend API

A FastAPI backend for fetching PyPI download statistics with PostgreSQL caching and failover support.

## ✨ Features

- **API Integration**: Fetches download stats from Pepy.tech API
- **Database Caching**: PostgreSQL storage with automatic fallback
- **Smart Failover**: Returns cached data when API is unavailable
- **Rate Limit Handling**: Graceful handling of API rate limits
- **Health Monitoring**: Comprehensive health checks and monitoring endpoints
- **Structured Logging**: Detailed request/response logging

## 🏗️ Architecture

```
backend/
├── main.py              # FastAPI app initialization
├── init_db.py           # Database setup script
├── requirements.txt     # Dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py      # Environment configuration
│   └── database.py      # Database connection & operations
├── models/
│   ├── __init__.py
│   └── schemas.py       # Pydantic models
├── services/
│   ├── __init__.py
│   └── pepy_service.py  # API service with caching logic
└── api/
    ├── __init__.py
    └── routes.py        # API endpoints
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment
Create a `.env` file:
```env
# Pepy.tech API Configuration
VITE_PEPPY_API_KEY=your_api_key_here

# Database Configuration (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jackofalltrades
DB_USER=postgres
DB_PASSWORD=password
```

### 3. Set up PostgreSQL
```bash
# Create database
createdb jackofalltrades

# Initialize tables
python init_db.py
```

### 4. Start the Server
```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 How It Works

### Request Flow
1. **API Request**: Frontend calls `/api/downloads`
2. **External API Call**: Backend calls Pepy.tech API
3. **Status Check**:
   - **200 OK**: Store response in database → Return to frontend
   - **Non-200**: Fetch latest cached data → Return to frontend
4. **Fallback**: If no cached data available, return error with details

### Database Schema
```sql
CREATE TABLE api_cache (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    response_data JSONB NOT NULL,
    status_code INTEGER NOT NULL,
    success BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

## 🔗 API Endpoints

### Core Endpoints
- `GET /` - Basic health check
- `GET /health` - Detailed health with database/API status
- `GET /api/downloads` - Download statistics (with caching)
- `GET /api/downloads/formatted` - Formatted download numbers
- `GET /ping` - Simple monitoring endpoint

### Monitoring Endpoints
- `GET /api/cache/status` - Cache statistics and recent entries
- `POST /api/cache/cleanup` - Clean up old cache entries
- `GET /api/database/test` - Test database connection

## 🔧 Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_PEPPY_API_KEY` | - | Pepy.tech API key |
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | jackofalltrades | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | password | Database password |

### CORS Origins
The API accepts requests from:
- `https://jackofalltrades-py.netlify.app`
- `http://localhost:3000`
- `http://localhost:5173`

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### Cache Status
```bash
curl http://localhost:8000/api/cache/status
```

### Database Test
```bash
curl http://localhost:8000/api/database/test
```

### Logs
The application provides detailed logging:
- Request timestamps
- API response status codes
- Cache hit/miss information
- Error details with stack traces

## 🐛 Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists: `createdb jackofalltrades`
4. Test connection: `python init_db.py`

### API Key Issues
1. Get API key from [Pepy.tech](https://pepy.tech)
2. Set in `.env` file: `VITE_PEPPY_API_KEY=your_key`
3. Verify in health check: `GET /health`

### CORS Issues
1. Check origin in `config/settings.py`
2. Verify frontend URL matches exactly
3. Check browser network tab for CORS errors

## 🚀 Deployment

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
```bash
# Production environment variables
export VITE_PEPPY_API_KEY="your_production_key"
export DB_HOST="your_postgres_host"
export DB_NAME="jackofalltrades_prod"
# ... other variables
```

## 📝 Example Response

### Successful API Response
```json
{
  "success": true,
  "total_downloads": 12345,
  "project_id": "jackofalltrades",
  "versions": [...],
  "last_updated": "2024-01-15T10:30:00Z",
  "cached": false
}
```

### Cached Response (API Failed)
```json
{
  "success": true,
  "total_downloads": 12000,
  "project_id": "jackofalltrades",
  "versions": [...],
  "last_updated": "2024-01-14T15:20:00Z",
  "cached": true,
  "cache_timestamp": "2024-01-14T15:20:00Z",
  "error": "API error (status 429), using cached data"
}
``` 