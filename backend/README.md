# Tony Dynamic Backend

FastAPI backend for the Tony Dynamic lucky number games platform.

## Features

- User authentication with JWT tokens
- Admin dashboard with round management
- Draw winning numbers and award prizes
- Paystack payment integration
- PostgreSQL database
- SQLAlchemy ORM with async support

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Local Development

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Update `.env` with your configuration:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tonydynamic
SECRET_KEY=your-secret-key-here
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Compose

```bash
docker-compose up
```

This starts PostgreSQL and the API server.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Rounds
- `GET /api/rounds/active` - Get active rounds
- `GET /api/rounds/{id}` - Get round details
- `POST /api/rounds/entry` - Join a round

### Admin
- `POST /api/admin/rounds/create` - Create new round
- `POST /api/admin/rounds/{id}/draw` - Draw winner and award prize
- `GET /api/admin/stats` - Get platform stats
- `GET /api/admin/rounds` - Get all rounds
- `PUT /api/admin/rounds/{id}/status` - Update round status

### Paystack
- `GET /api/paystack/verify` - Verify payment

## Admin Login

Default admin credentials:
- Username: `admin`
- Password: `admin123`

**Change these in production!**

## Database Schema

- `users` - User accounts and wallet data
- `rounds` - Game rounds
- `round_entries` - User entries in rounds
- `winners` - Winners and prizes
- `deposits` - Payment deposits

## Development

### Run with auto-reload:
```bash
uvicorn main:app --reload
```

### Database migrations:
The database is auto-created on startup. For production, use Alembic or similar.

## Testing

```bash
pytest
```
