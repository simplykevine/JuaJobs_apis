# JuaJobs API

A comprehensive RESTful API for the JuaJobs gig economy platform, connecting skilled workers with clients across Africa.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Job Postings**: Create, update, and manage job listings
- **Applications**: Apply for jobs with file uploads
- **Reviews**: Two-way review system for jobs
- **Skills & Categories**: Structured skill taxonomy
- **Payments**: Transaction tracking and management
- **Real-time**: WebSocket support for notifications
- **Security**: JWT authentication with role-based permissions
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🛠️ Tech Stack

- **Backend**: Django 5.2.3 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Documentation**: drf-spectacular (OpenAPI 3.1)
- **File Storage**: Django file handling
- **Caching**: Django cache framework
- **Testing**: Django Test Framework

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🔧 Installation & Setup

### 1. Clone the Repository
\`\`\`bash
git clone <repository-url>
cd jua-jobs-api
\`\`\`

### 2. Create Virtual Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Environment Setup
Create a `.env` file in the project root:
\`\`\`env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
\`\`\`

### 5. Database Setup
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
\`\`\`

### 6. Load Sample Data (Optional)
\`\`\`bash
python manage.py loaddata fixtures/sample_data.json
\`\`\`

### 7. Run Development Server
\`\`\`bash
python manage.py runserver
\`\`\`

The API will be available at `http://localhost:8000/api/`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Quick Start Examples

#### 1. User Registration
\`\`\`bash
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "worker"
  }'
\`\`\`

#### 2. User Login
\`\`\`bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
\`\`\`

#### 3. Create Job Posting (Client)
\`\`\`bash
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
    "remote_work": true
  }'
\`\`\`

#### 4. Apply for Job (Worker)
\`\`\`bash
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "job_id=1" \
  -F "cover_letter=@/path/to/cv.pdf"
\`\`\`

## 🏗️ Project Structure

\`\`\`
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
│       └── caching.py         # Cache utilities
├── jua_jobs/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/                     # User uploaded files
├── static/                    # Static files
├── requirements.txt           # Python dependencies
├── openapi.yaml              # API specification
└── README.md
\`\`\`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. After login, include the token in requests:

\`\`\`bash
Authorization: Bearer <your-jwt-token>
\`\`\`

### Token Refresh
\`\`\`bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
\`\`\`

## 👥 User Roles & Permissions

### Client Role
- Create and manage job postings
- View applications to their jobs
- Update application status
- Submit reviews for workers

### Worker Role
- Create and manage worker profile
- Apply for jobs
- View their applications
- Submit reviews for clients

### Permissions Matrix
| Resource | Guest | Worker | Client | Admin |
|----------|-------|---------|---------|--------|
| Jobs (List/View) | ✓ | ✓ | ✓ | ✓ |
| Jobs (Create) | ✗ | ✗ | ✓ | ✓ |
| Applications (Create) | ✗ | ✓ | ✗ | ✓ |
| Reviews (Create) | ✗ | Job Participant | Job Owner | ✓ |

## 🧪 Testing

### Run All Tests
\`\`\`bash
python manage.py test
\`\`\`

### Run Specific Test Module
\`\`\`bash
python manage.py test api.tests.test_models
\`\`\`

### Test Coverage
\`\`\`bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
\`\`\`

## 📊 API Endpoints Overview

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

### Dashboard
- `GET /api/dashboard/stats/` - User dashboard stats
- `GET /api/platform/stats/` - Platform statistics

## 🔍 Filtering & Search

### Job Filtering
\`\`\`bash
# Filter by status and location
GET /api/jobs/?status=active&location=Nairobi

# Search by title/description
GET /api/jobs/?search=python developer

# Filter by employment type and remote work
GET /api/jobs/?employment_type=full_time&remote_work=true

# Filter by skills
GET /api/jobs/?skills=Python,Django
\`\`\`

### Pagination
\`\`\`bash
# Get page 2 with 10 items per page
GET /api/jobs/?page=2&page_size=10
\`\`\`

## 🚀 Deployment

### Environment Variables
\`\`\`env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
\`\`\`

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure media file storage
- [ ] Set up SSL/HTTPS
- [ ] Configure caching (Redis)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

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

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/api/docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: api@juajobs.com

## 🔄 Changelog

### v1.0.0 (2025-06-16)
- Initial release
- User authentication and authorization
- Job posting and application system
- Review system
- Skills and categories management
- Payment transaction tracking
- Comprehensive API documentation

---

**Built with ❤️ for the African gig economy**
