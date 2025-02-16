# Avito Merch Shop

An internal merchandise shop system built with Flask, allowing employees to exchange coins and purchase merchandise.

## Features

- User authentication with automatic registration
- Coin-based transaction system between users
- Merchandise purchasing system
- REST API endpoints
- Web interface for user interaction

## Running with Docker Compose

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

3. Start the application:
```bash
docker-compose up --build
```

4. Access the application at `http://localhost:8080`

## Environment Variables

The following environment variables can be configured in the docker-compose.yaml file:

- `DATABASE_URL`: PostgreSQL database URL
- `SESSION_SECRET`: Secret key for session management
- `FLASK_DEBUG`: Enable/disable debug mode

## API Documentation

The API endpoints are available at:

- `POST /api/auth`: Authenticate and get JWT token
- `GET /api/info`: Get user information and transaction history
- `POST /api/sendCoin`: Send coins to another user
- `GET /api/buy/{item}`: Purchase merchandise

## Testing

The project includes:
- Unit tests
- Integration tests
- Load tests using Locust

To run the tests:
```bash
docker-compose exec web pytest
```

To run load tests:
```bash
docker-compose exec web locust -f tests/locustfile.py
```