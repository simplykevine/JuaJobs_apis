# JuaJobs API

A comprehensive RESTful API for the JuaJobs gig economy platform, connecting skilled workers with clients across Africa.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Job Postings**: Create, update, and manage job listings
- **Applications**: Apply for jobs with file uploads
- **Reviews**: Two-way review system for jobs
- **Skills & Categories**: Structured skill taxonomy
- **Payments**: Transaction tracking and management with African mobile money support
- **Real-time**: Caching and performance optimization
- **Security**: JWT authentication with role-based permissions
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🛠️ Tech Stack

- **Backend**: Django 5.2.3 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Cache**: Redis
- **Documentation**: drf-spectacular (OpenAPI 3.1)
- **File Storage**: Django file handling
- **Testing**: Django Test Framework

## 📋 Prerequisites

- Python 3.8+
- Redis (for caching)
- pip
- Virtual environment (recommended)

## 🔧 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd jua-jobs-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

### 2. Environment Configuration

Create a `.env` file in the project root directory:

```plaintext
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://127.0.0.1:6379/1
```

### 3. Database Setup

```shellscript
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 4. Start Redis Server

```shellscript
# Start Redis server (required for caching)
redis-server
```

### 5. Start Development Server

```shellscript
python manage.py runserver
```

🎉 **API is now running at:** `http://localhost:8000/api/`

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)


### Quick API Examples

#### User Registration

```shellscript
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "worker",
    "country": "KE",
    "phone_number": "+254712345678"
  }'
```

#### User Login

```shellscript
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

#### Create Job Posting

```shellscript
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer...",
    "salary_min": 1000.00,
    "salary_max": 2000.00,
    "employment_type": "full_time",
    "location": "Nairobi, Kenya",
    "remote_work": true,
    "category_id": 1,
    "skill_ids": [1, 2, 3]
  }'
```

#### Apply for Job

```shellscript
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "job_id=1" \
  -F "cover_letter=@/path/to/cv.pdf"
```

## 🏗️ Project Structure

```plaintext
jua-jobs-api/
├── api/                        # Main API application
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # URL routing
│   ├── permissions.py         # Custom permissions
│   ├── filters.py             # Query filters
│   ├── admin.py               # Django admin
│   ├── tests/                 # Test files
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   └── utils/
│       ├── caching.py         # Cache utilities
│       ├── african_validators.py # African market validators
│       └── batch_operations.py   # Batch processing
├── jua_jobs/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/                     # User uploaded files
├── static/                    # Static files
├── requirements.txt           # Python dependencies
└── README.md
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Using JWT Tokens

Include the token in request headers:

```shellscript
Authorization: Bearer <your-jwt-token>
```

### Token Refresh

```shellscript
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

## 👥 User Roles & Permissions

### Role Definitions

**Client Role**

- Create and manage job postings
- View applications to their jobs
- Update application status
- Submit reviews for workers


**Worker Role**

- Create and manage worker profile
- Apply for jobs
- View their applications
- Submit reviews for clients


### Permissions Matrix

| Resource | Guest | Worker | Client | Admin
|-----|-----|-----|-----|-----
| Jobs (List/View) | ✅ | ✅ | ✅ | ✅
| Jobs (Create) | ❌ | ❌ | ✅ | ✅
| Applications (Create) | ❌ | ✅ | ❌ | ✅
| Reviews (Create) | ❌ | ✅* | ✅* | ✅


*Only for job participants

## 📊 API Endpoints

### Authentication

- `POST /api/signup/` - User registration
- `POST /api/login/` - User login
- `POST /api/token/refresh/` - Refresh JWT token


### Users & Profiles

- `GET /api/users/` - List users
- `GET /api/users/me/` - Current user profile
- `GET /api/profiles/` - List worker profiles
- `POST /api/profiles/` - Create worker profile


### Jobs

- `GET /api/jobs/` - List jobs (with filters)
- `POST /api/jobs/` - Create job (clients only)
- `GET /api/jobs/{id}/` - Job details
- `PATCH /api/jobs/{id}/` - Update job
- `GET /api/jobs/my_jobs/` - Client's jobs


### Applications

- `GET /api/applications/` - List applications
- `POST /api/applications/` - Submit application
- `PATCH /api/applications/{id}/update_status/` - Update status


### Reviews

- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/user_reviews/` - User's reviews


### Skills & Categories

- `GET /api/skills/` - List skills
- `GET /api/categories/` - List categories


### Payments

- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `GET /api/payment-methods/` - List payment methods
- `POST /api/payment-methods/` - Add payment method


### Batch Operations

- `POST /api/batch/` - Execute multiple operations
- `POST /api/jobs/bulk/` - Bulk job upload


### Dashboard

- `GET /api/dashboard/stats/` - User dashboard stats
- `GET /api/platform/stats/` - Platform statistics


## 🔍 Filtering & Search

### Job Filtering Examples

```shellscript
# Filter by status and location
GET /api/jobs/?status=active&location=Nairobi

# Search by title/description
GET /api/jobs/?search=python developer

# Filter by employment type and remote work
GET /api/jobs/?employment_type=full_time&remote_work=true

# Filter by skills
GET /api/jobs/?skills=Python,Django

# Pagination
GET /api/jobs/?page=2&page_size=10
```

## 🌍 African Market Features

### Mobile Money Support

- M-Pesa (Kenya)
- Airtel Money (Kenya, Uganda, Tanzania)
- MTN Mobile Money (Uganda, South Africa)


### Phone Number Validation

- Kenya: `+254XXXXXXXXX`
- Nigeria: `+234XXXXXXXXXX`
- South Africa: `+27XXXXXXXXX`
- Uganda: `+256XXXXXXXXX`
- Tanzania: `+255XXXXXXXXX`


### Currency Support

- KES (Kenyan Shilling)
- NGN (Nigerian Naira)
- ZAR (South African Rand)
- UGX (Ugandan Shilling)
- TZS (Tanzanian Shilling)


## 🧪 Testing

### Run Tests

```shellscript
# Run all tests
python manage.py test

# Run specific test module
python manage.py test api.tests.test_models

# Test with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Coverage

The project includes comprehensive tests for:

- Models and validation
- Serializers
- API endpoints
- Authentication flows
- Permission logic
- African market features


## ⚡ Performance Features

### Caching

- Redis-based caching for frequently accessed data
- Cache invalidation strategies
- Query optimization


### Batch Operations

- Bulk job uploads
- Multiple API operations in single request
- Performance monitoring


### Compression

- Response compression enabled
- Optimized payload sizes


## 🚀 Deployment

### Production Environment Variables

```plaintext
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

### Production Checklist

- Set `DEBUG=False`
- Configure production database (PostgreSQL)
- Set up static file serving
- Configure media file storage
- Set up SSL/HTTPS
- Configure Redis caching
- Set up monitoring and logging
- Configure backup strategy


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Ensure all tests pass before submitting PR


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Resources

- **📖 Documentation**: API Docs ([http://localhost:8000/api/docs/](http://localhost:8000/api/docs/))
- **🐛 Issues**: GitHub Issues


## 🔄 Changelog

### v1.0.0 (2025-06-16)

- ✨ Initial release
- 🔐 User authentication and authorization
- 💼 Job posting and application system
- ⭐ Review system
- 🎯 Skills and categories management
- 💳 Payment transaction tracking with African mobile money
- 📚 Comprehensive API documentation
- ⚡ Redis caching and performance optimization
- 🌍 African market adaptations


---

**Built with ❤️ for the African gig economy**

> **Note**: This API is designed to empower African freelancers and businesses by providing a robust platform for connecting talent with opportunities across the continent.
