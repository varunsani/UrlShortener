# 🔗 URL Shortener

A fully asynchronous, production-ready URL shortener service built with **FastAPI**, **PostgreSQL**, and **Redis**. Converts long URLs into compact 6-character links, complete with JWT authentication, role-based access control, click analytics, Redis caching, and per-IP rate limiting.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Migrations](#database-migrations)
- [How It Works](#how-it-works)
  - [Authentication Flow](#authentication-flow)
  - [URL Shortening Flow](#url-shortening-flow)
  - [Redirect & Caching Flow](#redirect--caching-flow)
  - [Analytics Tracking](#analytics-tracking)
  - [Security Architecture](#security-architecture)
- [API Reference](#api-reference)
  - [Auth Endpoints](#auth-endpoints)
  - [URL Endpoints](#url-endpoints)
  - [Analytics Endpoints](#analytics-endpoints)
  - [Admin Endpoints](#admin-endpoints)
- [Rate Limiting](#rate-limiting)
- [Environment Variables](#environment-variables)
- [Error Handling](#error-handling)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## 🔍 Overview

This service transforms long, cumbersome URLs into concise, shareable short links while providing enterprise-grade features. Built on a fully asynchronous stack, it handles hundreds of concurrent requests efficiently — ideal for high-traffic use cases where speed and reliability matter.

---

## ✨ Features

- **URL Shortening** — generates unique 6-character base62 codes (A–Z, a–z, 0–9)
- **JWT Authentication** — short-lived access tokens (15 min) + long-lived refresh tokens (7 days)
- **Role-Based Access Control** — standard users vs. admin users with elevated privileges
- **Click Analytics** — tracks total, daily, weekly, and monthly click counts
- **Redis Caching** — popular redirects served from cache with a 1-hour TTL, slashing DB load
- **Token Blacklisting** — logout immediately invalidates tokens in Redis with precise TTL
- **Rate Limiting** — per-IP protection: 10 URL creations/min, 60 redirects/min
- **Fully Async Architecture** — built on FastAPI + asyncpg for maximum throughput
- **Database Migrations** — managed with Alembic for safe schema evolution
- **CORS Support** — configurable allowed origins

---

## 🛠 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | FastAPI | 0.104.1 |
| ASGI Server | Uvicorn | 0.24.0 |
| ORM | SQLAlchemy | 2.0.23 |
| Async DB Driver | asyncpg | 0.29.0 |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Migrations | Alembic | 1.12.1 |
| Auth (JWT) | python-jose | 3.3.0 |
| Password Hashing | bcrypt | 4.1.2 |
| Settings | pydantic-settings | 2.1.0 |
| Validation | pydantic | 2.5.0 |

---

## 📁 Project Structure

```
UrlShortener/
│
├── app/                        # Main application package
│   ├── __pycache__/
│   ├── dependencies/           # Dependency injection (auth, db, redis)
│   ├── middleware/             # Custom middleware (rate limiting, CORS)
│   ├── models/                 # SQLAlchemy ORM models
│   ├── routers/                # FastAPI route definitions
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility/helper functions
│   ├── __init__.py
│   ├── config.py               # App settings via pydantic-settings
│   ├── database.py             # Async DB engine and session setup
│   ├── main.py                 # App entry point, middleware registration
│   └── redis_client.py         # Redis connection and helper functions
│
├── migrations/                 # Alembic migration scripts
│   └── versions/
│
├── .env.example                # Sample environment variables
├── .gitignore
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

## ✅ Prerequisites

- **Python 3.10+** — https://www.python.org/downloads/
- **PostgreSQL 15+** — https://www.postgresql.org/download/
- **Redis 7+** — https://redis.io/download
- **Git** — https://git-scm.com/downloads

---

## 📦 Installation

**1. Clone the repository**

```bash
git clone https://github.com/varunsani/UrlShortener.git
cd UrlShortener
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

**1. Copy the example environment file**

```bash
cp .env.example .env
```

**2. Edit `.env` with your actual values**

```env
APP_NAME=URL Shortener
DEBUG=True
BASE_URL=http://localhost:8000

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener

# Redis
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_CREATE_URL=10
RATE_LIMIT_CLICK_URL=60
RATE_LIMIT_WINDOW_SECONDS=60

# URL Settings
SHORT_CODE_LENGTH=6

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Default Admin Account
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin123!
ADMIN_USERNAME=admin
```

> ⚠️ **Security Note:** Always change `SECRET_KEY` and the default admin credentials before deploying to production.

---

## 🚀 Running the Application

**1. Make sure PostgreSQL and Redis are running**

```bash
# PostgreSQL (Linux/macOS)
sudo service postgresql start

# Redis (Linux/macOS)
sudo service redis start
```

**2. Run database migrations**

```bash
alembic upgrade head
```

**3. Start the development server**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

**Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`

**Alternative Docs (ReDoc):** `http://localhost:8000/redoc`

---

## 🗄️ Database Migrations

This project uses **Alembic** to manage database schema changes.

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# View migration history
alembic history
```

---

## ⚙️ How It Works

### Authentication Flow

**Registration**

1. User submits email, username, and password.
2. The password is hashed with **bcrypt** and stored in PostgreSQL.
3. A default admin account is seeded on first startup using the values in `.env`.

**Login**

1. User provides credentials; the system validates them against the database.
2. Two JWT tokens are issued:
   - **Access Token** — expires in 15 minutes; used for all authenticated API calls.
   - **Refresh Token** — expires in 7 days; used only to obtain a new access token.
3. The refresh token is persisted in PostgreSQL to support rotation and revocation.

**Token Refresh**

1. Client sends the refresh token to `/auth/refresh`.
2. The system validates it, issues a new access token, and optionally rotates the refresh token.

**Logout**

1. The access token is blacklisted in Redis with a TTL matching the token's remaining validity.
2. The refresh token is deleted from the database.
3. The user is effectively logged out across all sessions.

---

### URL Shortening Flow

1. Authenticated user submits a long URL via `POST /urls/`.
2. The system generates a unique **6-character base62 code** (characters: `A–Z`, `a–z`, `0–9`).
3. The short code, original URL, and creator's user ID are saved in PostgreSQL.
4. The shortened URL (e.g., `http://localhost:8000/abc123`) is returned.

**Collision Handling:** If the generated code already exists, the system regenerates until a unique code is found.

---

### Redirect & Caching Flow

When a user visits a short URL (e.g., `GET /abc123`):

```
Request
   │
   ▼
Check Redis Cache
   │
   ├── Cache HIT  ──► Return original URL instantly
   │
   └── Cache MISS ──► Query PostgreSQL
                           │
                           ▼
                     Store in Redis (TTL: 1 hour)
                           │
                           ▼
                     Return original URL
                     + Increment click count (async)
```

This caching strategy dramatically reduces database load for popular short links, delivering sub-millisecond redirects on cache hits.

---

### Analytics Tracking

Every redirect triggers asynchronous analytics updates — no blocking the redirect itself.

Tracked metrics per short URL:

| Metric | Description |
|---|---|
| Total Clicks | Lifetime click count |
| Daily Clicks | Clicks in the current calendar day |
| Weekly Clicks | Clicks in the current week |
| Monthly Clicks | Clicks in the current month |
| Creator Stats | Per-user aggregated analytics |

Analytics are stored in PostgreSQL with proper indexing for fast aggregation queries.

---

### Security Architecture

| Layer | Mechanism |
|---|---|
| Password Storage | bcrypt hashing with appropriate work factor |
| API Authentication | JWT (HS256) — validated on every protected request |
| Token Revocation | Redis-based blacklist; TTL matches token expiry |
| Access Control | Role-based (user / admin) enforced per endpoint |
| Abuse Prevention | Per-IP rate limiting via Redis counters |
| CORS | Configurable allowed origins via `ALLOWED_ORIGINS` |

---

## 📡 API Reference

### Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Create a new user account | No |
| `POST` | `/auth/login` | Login and receive tokens | No |
| `POST` | `/auth/refresh` | Refresh access token | No (refresh token) |
| `POST` | `/auth/logout` | Blacklist tokens and log out | Yes |
| `GET` | `/auth/me` | Get current user's profile | Yes |

**Register — Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Login — Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Login — Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer"
}
```

---

### URL Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/urls/` | Create a short URL | Yes |
| `GET` | `/{short_code}` | Redirect to original URL | No |
| `GET` | `/urls/` | List all URLs created by the current user | Yes |
| `GET` | `/urls/{short_code}` | Get details of a specific short URL | Yes |
| `DELETE` | `/urls/{short_code}` | Delete a short URL | Yes (owner only) |

**Create Short URL — Request Body:**
```json
{
  "original_url": "https://www.example.com/some/very/long/path?query=value"
}
```

**Create Short URL — Response:**
```json
{
  "short_code": "abc123",
  "short_url": "http://localhost:8000/abc123",
  "original_url": "https://www.example.com/some/very/long/path?query=value",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Analytics Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/urls/{short_code}/analytics` | Get click analytics for a specific URL | Yes (owner) |
| `GET` | `/users/me/analytics` | Get aggregated analytics for the current user | Yes |

**Analytics Response:**
```json
{
  "short_code": "abc123",
  "total_clicks": 1523,
  "daily_clicks": 42,
  "weekly_clicks": 310,
  "monthly_clicks": 1250
}
```

---

### Admin Endpoints

> Requires admin role. Set via `ADMIN_EMAIL`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD` in `.env`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/urls` | View all short URLs across all users |
| `GET` | `/admin/analytics` | View system-wide aggregated usage metrics |
| `GET` | `/admin/users` | List all registered users |

---

## 🚦 Rate Limiting

Rate limiting is enforced per IP address using Redis counters with a sliding window.

| Endpoint Type | Default Limit | Window |
|---|---|---|
| URL Creation (`POST /urls/`) | 10 requests | 60 seconds |
| URL Redirects (`GET /{code}`) | 60 requests | 60 seconds |

When the limit is exceeded, the API returns:

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

HTTP Status: `429 Too Many Requests`

Limits are configurable via environment variables:
```env
RATE_LIMIT_CREATE_URL=10
RATE_LIMIT_CLICK_URL=60
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `URL Shortener` | Application name |
| `DEBUG` | `True` | Enable debug mode (set `False` in production) |
| `BASE_URL` | `http://localhost:8000` | Base URL used to construct short links |
| `SECRET_KEY` | — | JWT signing secret (must be changed) |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime in days |
| `DATABASE_URL` | — | PostgreSQL connection string (asyncpg) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `RATE_LIMIT_CREATE_URL` | `10` | Max URL creations per window per IP |
| `RATE_LIMIT_CLICK_URL` | `60` | Max redirects per window per IP |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit time window in seconds |
| `SHORT_CODE_LENGTH` | `6` | Length of the generated short code |
| `ALLOWED_ORIGINS` | — | Comma-separated list of allowed CORS origins |
| `ADMIN_EMAIL` | — | Default admin email (seeded on startup) |
| `ADMIN_PASSWORD` | — | Default admin password |
| `ADMIN_USERNAME` | — | Default admin username |

---

## 🛡️ Error Handling

| HTTP Status | Scenario |
|---|---|
| `400 Bad Request` | Invalid URL format or missing required fields |
| `401 Unauthorized` | Missing, expired, or blacklisted JWT token |
| `403 Forbidden` | Authenticated but insufficient permissions (e.g., non-admin accessing `/admin/*`) |
| `404 Not Found` | Short code does not exist in the database |
| `409 Conflict` | Username or email already registered |
| `422 Unprocessable Entity` | Request body fails Pydantic validation |
| `429 Too Many Requests` | Per-IP rate limit exceeded |
| `500 Internal Server Error` | Unexpected server-side error |

---

## ⚠️ Limitations

- **No custom aliases** — short codes are auto-generated; users cannot choose their own.
- **No link expiration** — short URLs do not expire unless manually deleted.
- **Single-region** — no built-in support for multi-region deployment or geo-routing.
- **No web UI** — the application is API-only; a frontend is not included.
- **No SSL out of the box** — HTTPS must be configured via a reverse proxy (e.g., Nginx, Caddy).
- **No email verification** — user registration does not require email confirmation.

---

## 🚧 Future Improvements

- [ ] Custom short code aliases (vanity URLs)
- [ ] Link expiration with configurable TTL per URL
- [ ] QR code generation for each short URL
- [ ] Web frontend (React / Next.js)
- [ ] Docker + Docker Compose setup for one-command deployment
- [ ] Email verification on registration
- [ ] Password reset via email
- [ ] Geo-analytics (click location by country/region)
- [ ] Webhook support — notify external services on each redirect
- [ ] Bulk URL import via CSV
- [ ] OpenAPI schema export for third-party client generation

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

