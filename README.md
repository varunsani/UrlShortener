# 🔗 URL Shortener - Complete Production-Ready Application

A fully asynchronous, production-ready URL shortener service built with **FastAPI**, **PostgreSQL**, and **Redis**. Features include JWT authentication, role-based access control, comprehensive analytics, rate limiting, and intelligent Redis caching.

---

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Complete Setup Guide](#complete-setup-guide)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing with Postman](#testing-with-postman)
- [How It Works](#how-it-works)
- [Redis Commands](#redis-commands)
- [PostgreSQL Commands](#postgresql-commands)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Auth**: python-jose 3.3.0 (JWT)
- **Password Hashing**: bcrypt 4.1.2
- **Migrations**: Alembic 1.12.1
- **Async Driver**: asyncpg 0.29.0
- **Server**: Uvicorn 0.24.0

---

## ✨ Features

- URL Shortening with 6-character base62 codes
- JWT Authentication (Access tokens 15 min, Refresh tokens 7 days)
- Role-Based Access Control (admin/user)
- Click Analytics (total/daily/weekly/monthly)
- Redis Caching (1 hour TTL on first access)
- Rate Limiting (10 creations/min, 60 redirects/min per IP)
- Token Blacklisting with exact TTL
- Fully Async Architecture
- CORS Support

---

## 📋 Prerequisites

- Python 3.10+ (https://www.python.org/downloads/)
- PostgreSQL 15+ (https://www.postgresql.org/download/)
- Redis 7+ (https://redis.io/download)
- Git (https://git-scm.com/downloads)

---

## 🚀 Complete Setup Guide

### Step 1: Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/varunsani/UrlShortener.git
cd url-shortener

# Create virtual environment
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt