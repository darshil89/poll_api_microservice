# API Microservice

A high-performance poll management microservice built with FastAPI, MongoDB, Redis, and Socket.IO. This service handles poll creation, voting, real-time updates, and provides WebSocket support for live poll interactions.

## 🚀 Features

- **Poll Management**: Create, retrieve, and manage polls with options
- **Real-time Voting**: Live vote counting and updates via WebSocket
- **Like System**: Users can like/unlike polls with real-time updates
- **Authentication**: JWT-based authentication middleware
- **Caching**: Redis-based caching for high-performance vote counting
- **WebSocket Support**: Real-time communication via Socket.IO
- **Database Integration**: MongoDB with Prisma ORM
- **Message Queue**: Redis pub/sub for real-time updates
- **CORS Support**: Cross-origin resource sharing enabled

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Database**: MongoDB
- **Cache/Queue**: Redis
- **ORM**: Prisma Client Python
- **WebSocket**: Socket.IO
- **Authentication**: JWT (PyJWT)
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Environment**: Python-dotenv

## 📁 Project Structure

```
api_microservice/
├── controllers/                      # Business logic controllers
│   ├── __init__.py                  # Package initialization
│   └── poll.py                      # Poll management logic
├── helpers/                         # Utility and helper functions
│   ├── auth_middleware.py           # JWT authentication middleware
│   ├── db.py                        # Database and Redis connection utilities
│   └── jwt_auth.py                  # JWT token validation
├── models/                          # Pydantic data models
│   └── poll.py                      # Poll, Option, Vote, Like models
├── prisma/                          # Database schema and configuration
│   └── schema.prisma                # Prisma database schema
├── router/                          # FastAPI route definitions
│   ├── __init__.py                  # Package initialization
│   └── poll.py                      # Poll API routes
├── main.py                          # FastAPI application entry point
└── requirements.txt                 # Python dependencies
```

## 🚦 Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB instance running
- Redis instance running
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api_microservice
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   
   Create a `.env` file in the root directory:
   ```env
   API_DATABASE_URL="mongodb://localhost:27017/quickpoll_api"
   API_REDIS_HOST="localhost"
   API_REDIS_PORT="6379"
   API_REDIS_PASSWORD=""
   JWT_SECRET_KEY="your-super-secret-jwt-key-here"
   ```

5. **Generate Prisma Client**
   ```bash
   prisma generate
   ```

6. **Start the development server**
   ```bash
   python main.py
   ```

7. **Verify the service**
   
   The service will be available at `http://localhost:8001`
   
   Check the health endpoint: `GET http://localhost:8001/`

## 📜 API Endpoints

### Poll Management Routes

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/poll/create-poll` | Create a new poll | Required |
| `GET` | `/api/poll/get-poll-by-id/{poll_id}` | Get poll by ID | Required |
| `GET` | `/api/poll/get-poll-by-user-id/{user_id}` | Get user's polls | Required |
| `GET` | `/api/poll/get-all-polls` | Get all polls | Required |
| `POST` | `/api/poll/vote-on-poll/{poll_id}/{option_id}` | Vote on a poll | Required |
| `POST` | `/api/poll/like-poll/{poll_id}` | Like a poll | Required |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/ws/updates` | WebSocket connection for real-time updates |

### Request/Response Examples

#### Create Poll
```http
POST /api/poll/create-poll
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "question": "What's your favorite programming language?",
  "options": [
    {"text": "Python"},
    {"text": "JavaScript"},
    {"text": "TypeScript"},
    {"text": "Go"}
  ]
}
```

**Response:**
```json
{
  "id": "poll_id_here",
  "question": "What's your favorite programming language?",
  "userId": "user_id_here",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### Get Poll by ID
```http
GET /api/poll/get-poll-by-id/poll_id_here
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "poll_id_here",
  "question": "What's your favorite programming language?",
  "userId": "user_id_here",
  "createdAt": "2024-01-01T00:00:00Z",
  "options": [
    {
      "id": "option_1",
      "text": "Python",
      "pollId": "poll_id_here"
    }
  ],
  "counts": {
    "likes": 5,
    "option_1": 10,
    "option_2": 8
  },
  "userHasVoted": "option_1",
  "userHasLiked": true
}
```

#### Vote on Poll
```http
POST /api/poll/vote-on-poll/poll_id_here/option_id_here
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "vote_id_here",
  "userId": "user_id_here",
  "optionId": "option_id_here",
  "pollId": "poll_id_here"
}
```

## 🏗️ Architecture Overview

### Database Schema

The service uses MongoDB with the following models:

```prisma
model Poll {
  id        String   @id @default(auto()) @map("_id") @db.ObjectId
  question  String
  userId    String   @db.ObjectId
  createdAt DateTime @default(now())
  options   Option[]
  votes     Vote[]
  likes     Like[]
}

model Option {
  id     String @id @default(auto()) @map("_id") @db.ObjectId
  text   String
  pollId String @db.ObjectId
  poll   Poll   @relation(fields: [pollId], references: [id])
  votes  Vote[]
}

model Vote {
  id       String @id @default(auto()) @map("_id") @db.ObjectId
  userId   String @db.ObjectId
  optionId String @db.ObjectId
  pollId   String @db.ObjectId
  option   Option @relation(fields: [optionId], references: [id])
  poll     Poll   @relation(fields: [pollId], references: [id])
  @@unique([userId, pollId])
}

model Like {
  id     String @id @default(auto()) @map("_id") @db.ObjectId
  userId String @db.ObjectId
  pollId String @db.ObjectId
  poll   Poll   @relation(fields: [pollId], references: [id])
  @@unique([userId, pollId])
}
```

### Real-time Updates Flow

1. **User Action**: User votes or likes a poll
2. **Database Update**: Action is saved to MongoDB
3. **Redis Update**: Vote/like count is incremented in Redis
4. **Message Queue**: Update is published to Redis pub/sub
5. **WebSocket Broadcast**: All connected clients receive real-time update

### Caching Strategy

- **Vote Counts**: Stored in Redis with keys like `poll:{poll_id}:option:{option_id}`
- **Like Counts**: Stored in Redis with keys like `poll:{poll_id}:likes`
- **Batch Operations**: Multiple Redis keys are fetched in single `MGET` operation
- **Real-time Sync**: Redis pub/sub ensures all instances stay synchronized

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `API_DATABASE_URL` | MongoDB connection string | Yes | - |
| `API_REDIS_HOST` | Redis host | Yes | localhost |
| `API_REDIS_PORT` | Redis port | Yes | 6379 |
| `API_REDIS_PASSWORD` | Redis password | No | - |
| `JWT_SECRET_KEY` | Secret key for JWT validation | Yes | - |

### CORS Configuration

The service is configured to allow:
- All origins (`*`)
- All methods (`*`)
- All headers (`*`)
- Credentials enabled

### WebSocket Configuration

- **Path**: `/ws/updates`
- **CORS**: Enabled for all origins
- **Events**: `vote-update`, `like-update`

## 🚀 Deployment

### Production Build

1. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export API_DATABASE_URL="your-production-mongodb-url"
   export API_REDIS_HOST="your-redis-host"
   export API_REDIS_PORT="6379"
   export JWT_SECRET_KEY="your-production-secret-key"
   ```

3. **Generate Prisma Client**
   ```bash
   prisma generate
   ```

4. **Run with Uvicorn**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN prisma generate

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🧪 Development

### Code Structure Guidelines

- **Controllers**: Business logic and database operations
- **Routes**: API endpoint definitions and request handling
- **Models**: Pydantic models for data validation
- **Helpers**: Utility functions, authentication, and database connections

### Adding New Features

1. **Create Models**: Define Pydantic models in `models/`
2. **Add Controllers**: Implement business logic in `controllers/`
3. **Define Routes**: Create API endpoints in `router/`
4. **Update Main**: Register new routers in `main.py`

### WebSocket Events

The service emits the following WebSocket events:

- **`vote-update`**: When a user votes on a poll
- **`like-update`**: When a user likes/unlikes a poll

### Redis Operations

```python
# Increment vote count
await redis_client.incr(f"poll:{poll_id}:option:{option_id}")

# Get multiple counts
counts = await redis_client.mget([
    f"poll:{poll_id}:likes",
    f"poll:{poll_id}:option:{option_id}"
])

# Publish update
await redis_client.publish("poll-updates", json.dumps(data))
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MongoDB is running
   - Check `API_DATABASE_URL` environment variable
   - Ensure network connectivity

2. **Redis Connection Failed**
   - Verify Redis is running
   - Check Redis host, port, and password
   - Test Redis connection manually

3. **JWT Validation Error**
   - Ensure `JWT_SECRET_KEY` matches auth service
   - Check token format and expiration

4. **WebSocket Connection Issues**
   - Verify CORS configuration
   - Check Socket.IO client implementation
   - Test WebSocket endpoint manually

### Debug Mode

Enable debug logging by setting the log level:

```bash
export LOG_LEVEL=DEBUG
```

### Health Checks

Monitor service health:

```bash
# API health
curl http://localhost:8001/

# Database health (check logs)
# Redis health (check logs)
```

## 📊 Performance Considerations

### Redis Caching

- **Vote Counts**: Cached in Redis for fast retrieval
- **Batch Operations**: Multiple Redis operations in single call
- **Memory Usage**: Monitor Redis memory usage

### Database Optimization

- **Indexes**: Unique indexes on `(userId, pollId)` for votes and likes
- **Queries**: Optimized queries with proper includes
- **Connection Pooling**: Prisma handles connection pooling

### WebSocket Scaling

- **Redis Pub/Sub**: Enables horizontal scaling
- **Load Balancing**: Use sticky sessions for WebSocket connections
- **Message Queuing**: Redis pub/sub handles message distribution

## 📝 API Documentation

Once the service is running, you can access:

- **Interactive API Docs**: `http://localhost:8001/docs`
- **ReDoc Documentation**: `http://localhost:8001/redoc`
- **OpenAPI Schema**: `http://localhost:8001/openapi.json`

## 🔒 Security Considerations

- **JWT Validation**: All endpoints require valid JWT tokens
- **User Authorization**: Users can only access their own polls
- **Input Validation**: Pydantic models validate all inputs
- **Rate Limiting**: Consider implementing rate limiting for voting
- **HTTPS**: Use HTTPS in production environments

## 📈 Monitoring

### Key Metrics

- **Vote Counts**: Monitor Redis vote count accuracy
- **WebSocket Connections**: Track active connections
- **Database Performance**: Monitor query response times
- **Redis Performance**: Monitor cache hit rates

### Logging

The service logs:
- Database connection status
- Redis connection status
- WebSocket events
- Error messages and stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is part of the QuickPoll microservices architecture.

---

**API Microservice** - Built with ❤️ using FastAPI, Redis, and Socket.IO
