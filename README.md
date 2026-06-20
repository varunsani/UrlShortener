# 🔗 URL Shortener - Complete Production-Ready Application

A fully asynchronous, production-ready URL shortener service built with **FastAPI**, **PostgreSQL**, and **Redis**. Features include JWT authentication, role-based access control, comprehensive analytics, rate limiting, and intelligent Redis caching.

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Database Migrations (Alembic)](#database-migrations-alembic)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing with Postman](#testing-with-postman)
- [How It Works](#how-it-works)
  - [Authentication Flow](#authentication-flow)
  - [URL Shortening & Redirect Flow](#url-shortening--redirect-flow)
  - [Caching Strategy](#caching-strategy)
  - [Rate Limiting](#rate-limiting)
  - [Analytics Tracking](#analytics-tracking)
- [Redis Commands for Debugging](#redis-commands-for-debugging)
- [PostgreSQL Commands](#postgresql-commands)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [License](#license)

---

## 🛠 Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | Async web framework |
| **ORM** | SQLAlchemy | 2.0.23 | Database ORM with async support |
| **Database** | PostgreSQL | 16/17 | Primary data storage |
| **Cache** | Redis | 7+ | Caching & rate limiting |
| **Auth** | python-jose | 3.3.0 | JWT token handling |
| **Password Hashing** | bcrypt | 4.1.2 | Secure password storage |
| **Migrations** | Alembic | 1.12.1 | Database schema version control |
| **Async Driver** | asyncpg | 0.29.0 | Async PostgreSQL driver |
| **Server** | Uvicorn | 0.24.0 | ASGI server |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **URL Shortening** | Convert long URLs into short, memorable 6-character codes (base62: a-z, A-Z, 0-9) |
| **JWT Authentication** | Access tokens (15 min) + Refresh tokens (7 days) with rotation |
| **Role-Based Access** | `admin` (view all) and `user` (view own only) |
| **Click Analytics** | Track total clicks with daily/weekly/monthly breakdown |
| **Redis Caching** | Cache popular URLs for 1 hour after first access (not on creation) |
| **Rate Limiting** | 10 URL creations / 60 clicks per minute per IP |
| **Token Blacklisting** | Revoked refresh tokens stored in Redis with exact remaining TTL |
| **Async Architecture** | Fully async using asyncpg and redis.asyncio for maximum performance |
| **CORS Support** | Configurable allowed origins |


---

