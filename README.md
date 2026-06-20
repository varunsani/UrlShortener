# 🔗 URL Shortener - Complete Production-Ready Application

A fully asynchronous, production-ready URL shortener service built with FastAPI, PostgreSQL, and Redis. Features include JWT authentication, role-based access control, comprehensive analytics, rate limiting, and intelligent Redis caching.

## 🚀 Project Overview & Architecture

### What This Project Does

This URL shortener service transforms long, cumbersome URLs into concise, shareable links while providing enterprise-grade features like user authentication, detailed analytics, and performance optimization through intelligent caching.

### The Complete Flow

**1. User Registration & Authentication**

When a new user signs up, the system securely hashes their password using bcrypt and stores their credentials in PostgreSQL. Upon login, the system generates two JWT tokens:
- **Access Token** (valid for 15 minutes) - used for authenticated operations
- **Refresh Token** (valid for 7 days) - used to obtain new access tokens without re-authentication

The system stores refresh tokens in the database to enable secure token rotation and invalidation when needed.

**2. URL Shortening Process**

An authenticated user submits a long URL to the system. The service:
- Generates a unique 6-character code using base62 encoding (A-Z, a-z, 0-9)
- Stores the mapping between this short code and the original URL in PostgreSQL
- Adds the user's ID as the creator for ownership tracking
- Returns the shortened URL (e.g., `https://yourdomain.com/abc123`)

The system applies rate limiting per IP address to prevent abuse, allowing up to 10 new short URLs per minute.

**3. Redirect Flow with Smart Caching**

When a user visits a shortened URL:
- The system first checks Redis cache for the original URL
- If found (cache hit), it returns the URL instantly without database query
- If not found (cache miss), it queries PostgreSQL, stores the result in Redis with a 1-hour TTL, and returns the URL
- The system increments click analytics asynchronously without blocking the redirect

This caching strategy dramatically reduces database load and improves response times for popular links.

**4. Analytics Tracking**

Every redirect triggers comprehensive analytics collection:
- **Total clicks** - lifetime count
- **Daily, Weekly, Monthly** breakdowns
- **User-specific analytics** - track which users are creating the most popular links
- **Timestamp tracking** for trend analysis and reporting

Analytics are stored in PostgreSQL with proper indexing for fast aggregation queries.

**5. Security Architecture**

The application implements multiple security layers:
- **JWT Token Validation** - every protected endpoint verifies token signature and expiration
- **Role-Based Access Control** - admin users have elevated privileges for monitoring
- **Token Blacklisting** - upon logout, access tokens are blacklisted in Redis with exact TTL matching the token's remaining validity
- **Rate Limiting** - per-IP limits prevent DDoS attacks and API abuse
- **Password Hashing** - bcrypt with appropriate work factor for secure password storage

**6. Data Flow & Processing**
- Client Request → FastAPI Router → Middleware (Auth/Rate Limit) → Service Layer → Repository Layer → Database/Cache


- **Middleware Layer** - handles CORS, rate limiting, authentication
- **Service Layer** - business logic, token generation, URL creation, analytics
- **Repository Layer** - database operations, Redis caching logic
- **Database Layer** - PostgreSQL for persistence, Redis for caching

**7. Admin Capabilities**

Administrators gain access to:
- View all shortened URLs across all users
- Monitor system analytics and usage patterns
- Access aggregated metrics and performance data

### Why This Architecture Works

The asynchronous design using FastAPI and asyncpg ensures the application handles hundreds of concurrent requests efficiently. Redis caching reduces database queries by caching the most frequently accessed URLs. JWT-based authentication provides stateless, scalable user management, while PostgreSQL provides ACID compliance for critical data like user accounts and URL mappings.

The combination of short-lived access tokens with long-lived refresh tokens balances security with user experience. Token blacklisting in Redis ensures immediate revocation when needed, while the blacklist expiration matches the token's lifespan, preventing unlimited memory growth.

This architecture is battle-tested and ready for production deployment with proper monitoring, logging, and scaling strategies in place.

---

## 🛠 Tech Stack

**Framework:** FastAPI 0.104.1  
**ORM:** SQLAlchemy 2.0.23  
**Database:** PostgreSQL 15+  
**Cache:** Redis 7+  
**Auth:** python-jose 3.3.0 (JWT)  
**Password Hashing:** bcrypt 4.1.2  
**Migrations:** Alembic 1.12.1  
**Async Driver:** asyncpg 0.29.0  
**Server:** Uvicorn 0.24.0

## 📋 Prerequisites

**Python 3.10+** (https://www.python.org/downloads/)  
**PostgreSQL 15+** (https://www.postgresql.org/download/)  
**Redis 7+** (https://redis.io/download)  
**Git** (https://git-scm.com/downloads)

## ✨ Features

- **URL Shortening** with 6-character base62 codes
- **JWT Authentication** (Access tokens 15 min, Refresh tokens 7 days)
- **Role-Based Access Control** (admin/user)
- **Click Analytics** (total/daily/weekly/monthly)
- **Redis Caching** (1 hour TTL on first access)
- **Rate Limiting** (10 creations/min, 60 redirects/min per IP)
- **Token Blacklisting** with exact TTL
- **Fully Async Architecture**
- **CORS Support**

---