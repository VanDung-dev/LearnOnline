# AGENTS.md - LearnOnline Project Structure Documentation

> Tài liệu mô tả cấu trúc dự án LearnOnline - Django-based Learning Management System

## Tổng Quan Dự Án

**LearnOnline** là một hệ thống quản lý học tập (LMS) được xây dựng bằng Django 5.2.10, hỗ trợ đa trường học (multi-tenant), thanh toán trực tuyến, API RESTful, và hệ thống thảo luận.

### Tech Stack
- **Backend**: Django 5.2.10, Django REST Framework
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Cache/Session**: Database Cache (có thể nâng cấp lên Redis)
- **Task Queue**: Celery + Redis
- **Authentication**: Session + JWT (API)
- **Frontend**: Django Templates + Vanilla JS
- **Payment**: Mock/Stripe/VNPay/MoMo (configurable)

---

## Cấu Trúc Thư Mục

```
LearnOnline/
├── AGENTS.md                    # Tài liệu cấu trúc dự án (file này)
├── TODO.md                      # Kế hoạch nâng cấp và cải tiến
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── DjangoProject/               # Django project configuration
│   ├── __init__.py
│   ├── settings.py              # Main settings (SQLite default)
│   ├── settings_docker.py       # Docker-specific settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI config
│   ├── asgi.py                  # ASGI config
│   └── celery.py                # Celery configuration
│
├── apps/                        # All Django applications
│   ├── accounts/                # User management & authentication
│   ├── analytics/               # Analytics & tracking
│   ├── api/                     # REST API endpoints
│   ├── courses/                 # Course management (main app)
│   ├── discussions/             # Discussion forums
│   ├── notifications/           # Notification system
│   ├── organization/            # Multi-tenant school management
│   └── payments/                # Payment processing
│
├── templates/                   # Global templates
│   ├── base.html
│   ├── accounts/
│   ├── courses/
│   ├── discussions/
│   ├── notifications/
│   └── payments/
│
├── static/                      # Static files (CSS, JS, images)
│   ├── base.css
│   ├── base.js
│   ├── accounts/
│   ├── courses/
│   ├── discussions/
│   └── payments/
│
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│
├── docs/                        # Documentation
│   └── diagrams/
│
└── scripts/                     # Utility scripts
    ├── db_backup.py
    ├── db_restore.py
    ├── load_sample_data.py
    └── sample/                  # Sample data fixtures
```

---

## Chi Tiết Từng Application

### 1. `apps/accounts/` - Quản Lý Tài Khoản

| File | Mô Tả |
|------|-------|
| `models.py` | Profile model (extend User), CustomUserManager |
| `views.py` | Login, Register, Profile, Dashboard (7408 bytes) |
| `forms.py` | User registration & profile forms |
| `urls.py` | Auth routes |
| `middleware.py` | Custom middleware |
| `admin_middleware.py` | Admin access control |
| `signals.py` | Django signals (auto-create profile) |
| `tasks.py` | Celery tasks (2360 bytes) |
| `tests.py` | Unit tests (7224 bytes) |
| `migrations/` | Database migrations |

**Models chính:**
- `Profile` - Mở rộng User với bio, location, role, school

---

### 2. `apps/courses/` - Quản Lý Khóa Học (MAIN APP)

| File | Mô Tả | Size |
|------|-------|------|
| `models.py` | Course, Section, Subsection, Lesson, Quiz, Enrollment, Progress, Certificate | 18KB |
| `forms.py` | Course & Lesson forms | 9KB |
| `urls.py` | Course routes | 4KB |
| `views.py` | Main views (entry point) | 2.4KB |
| `utils.py` | Utility functions (WebP conversion) | 2KB |
| `tasks.py` | Celery tasks | 864B |
| `tests.py` | Unit tests | 6.7KB |
| `admin.py` | Admin configuration | 1.4KB |

#### Thư mục `includes/` - Views chi tiết (VẤN ĐỀ CẦN CẢI THIỆN)

| File | Mô Tả | Size |
|------|-------|------|
| `views_certificate.py` | Certificate views | 2.1KB |
| `views_course.py` | Course CRUD views | 13.3KB |
| `views_error.py` | Custom error handlers | 3KB |
| `views_lesson_detail.py` | Lesson detail views | 22KB |
| `views_lesson.py` | Lesson CRUD views | 14.9KB |
| `views_other.py` | Miscellaneous views | 5.3KB |
| `views_reorder.py` | Reorder views | 6.4KB |
| `views_search.py` | Search autocomplete | 1.7KB |
| `views_section.py` | Section CRUD views | 5.2KB |
| `views_subsection.py` | Subsection CRUD views | 5.6KB |

**Models chính:**
- `Category` - Danh mục khóa học
- `Course` - Khóa học
- `Section` - Chương/Phần
- `Subsection` - Phần con
- `Lesson` - Bài học (text/video/quiz)
- `Quiz`, `Question`, `Answer` - Hệ thống câu hỏi
- `QuizAttempt`, `UserAnswer` - Lịch sử làm bài
- `Enrollment` - Ghi danh
- `Progress` - Tiến độ học
- `Certificate` - Chứng chỉ
- `SearchQuery` - Lịch sử tìm kiếm

#### Thư mục `services/`
- `search_service.py` - Search business logic

#### Thư mục `templatetags/`
- `courses_extras.py` - Custom template filters

---

### 3. `apps/api/` - REST API

| File | Mô Tả | Size |
|------|-------|------|
| `views.py` | All API views (CẦN TÁCH NHỎ) | 27.8KB |
| `serializers.py` | DRF serializers | 13.8KB |
| `urls.py` | API routes | 5.1KB |
| `permissions.py` | Custom permissions | 2.3KB |
| `pagination.py` | Custom pagination | 680B |
| `search_views.py` | Search API | 13.1KB |
| `search_serializers.py` | Search serializers | 4.2KB |
| `tests.py` | API tests | 6.7KB |
| `test_search.py` | Search tests | 13.1KB |

**Endpoints chính:**
- `/api/auth/` - Authentication (register, login, profile)
- `/api/courses/` - Courses CRUD
- `/api/enrollments/` - Enrollments
- `/api/progress/` - Progress tracking
- `/api/discussions/` - Discussions
- `/api/admin/` - Admin endpoints

---

### 4. `apps/payments/` - Thanh Toán

| File | Mô Tả | Size |
|------|-------|------|
| `views.py` | Payment views | 19.5KB |
| `models.py` | Payment, PaymentLog | 3KB |
| `urls.py` | Payment routes | 756B |
| `admin.py` | Admin configuration | 1.5KB |
| `tests.py` | Payment tests | 10.1KB |

#### Thư mục `services/`
- `payment_service.py` - Payment business logic (4KB)

**Models chính:**
- `Payment` - Giao dịch thanh toán
- `PaymentLog` - Audit trail

---

### 5. `apps/organization/` - Multi-Tenant School

| File | Mô Tả | Size |
|------|-------|------|
| `models.py` | School, InstructorInvite | 2.3KB |
| `admin.py` | Admin configuration | 1.6KB |
| `middleware.py` | School access control | 1.6KB |
| `apps.py` | App configuration | 195B |

**Models chính:**
- `School` - Trường học (multi-tenant)
- `InstructorInvite` - Mời giảng viên

---

### 6. `apps/discussions/` - Thảo Luận

| File | Mô Tả | Size |
|------|-------|------|
| `views.py` | Discussion views | 7.1KB |
| `models.py` | Discussion, Reply, Vote | 2.4KB |
| `forms.py` | Discussion forms | 696B |
| `urls.py` | Discussion routes | 458B |
| `tests.py` | Discussion tests | 4KB |

**Models chính:**
- `Discussion` - Chủ đề thảo luận
- `Reply` - Trả lời (nested)
- `Vote` - Bình chọn

---

### 7. `apps/notifications/` - Thông Báo

| File | Mô Tả | Size |
|------|-------|------|
| `views.py` | Notification views | 864B |
| `api_views.py` | API views | 1.2KB |
| `models.py` | Notification model | 940B |
| `services.py` | Notification service | 406B |
| `serializers.py` | DRF serializers | 275B |
| `urls.py` | Notification routes | 518B |
| `tests.py` | Notification tests | 1.6KB |

**Models chính:**
- `Notification` - Thông báo (system/course/payment/discussion)

---

### 8. `apps/analytics/` - Phân Tích

| File | Mô Tả | Size |
|------|-------|------|
| `services.py` | Analytics services | 2.3KB |
| `api_views.py` | Analytics API | 759B |
| `urls.py` | Analytics routes | 328B |
| `tests.py` | Analytics tests | 2.2KB |

---

## URL Routing

### Root URLs (`DjangoProject/urls.py`)

| Path | Application |
|------|-------------|
| `/admin/` | Django Admin |
| `/dashboard/` | User Dashboard (accounts) |
| `/payments/` | Payments |
| `/notifications/` | Notifications |
| `/analytics/` | Analytics |
| `/` (root) | Courses + Accounts + Discussions |
| `/api/` | REST API |
| `/tinymce/` | TinyMCE |

### Custom Error Handlers
Tất cả error handlers được định nghĩa trong `apps/courses/views.py`:
- 404, 500, 403, 400, 405, 408, 429, 502, 503, 504

---

## Database Schema

### Quan Hệ Chính

```
School (1) ──── (N) Profile
School (1) ──── (N) InstructorInvite

Category (1) ──── (N) Course
User (1) ──── (N) Course (instructor)

Course (1) ──── (N) Section
Section (1) ──── (N) Subsection
Section (1) ──── (N) Lesson
Subsection (1) ──── (N) Lesson

Lesson (1) ──── (1) Quiz
Quiz (1) ──── (N) Question
Question (1) ──── (N) Answer

User (N) ──── (N) Course (via Enrollment)
User (N) ──── (N) Lesson (via Progress)

User (N) ──── (N) Course (via Certificate)

User (N) ──── (N) Payment
Payment (1) ──── (N) PaymentLog

Course (1) ──── (N) Discussion
Discussion (1) ──── (N) Reply
Reply (1) ──── (N) Reply (nested, via parent)

User (N) ──── (N) Notification
```

---

## Configuration

### Environment Variables (`.env`)

| Variable | Mô Tả |
|----------|-------|
| `SECRET_KEY` | Django secret key |
| `DEBUG_DJANGO` | Debug mode (True/False) |
| `ALLOWED_HOSTS` | Comma-separated hosts |
| `PAYMENTS_DRIVER` | Payment driver (mock/stripe/vnpay/momo) |
| `PAYMENTS_WEBHOOK_SECRET` | Webhook secret |
| `STRIPE_SECRET_KEY` | Stripe API key |
| `VNPAY_TMN_CODE` | VNPay merchant code |
| `VNPAY_HASH_SECRET` | VNPay hash secret |

### Settings Files

| File | Mục Đích |
|------|----------|
| `settings.py` | Main settings (SQLite default) |
| `settings_docker.py` | Docker-specific settings |
| `.env.postgresql.example` | PostgreSQL config template |

---

## Testing

### Test Files

| App | Test File | Size |
|-----|-----------|------|
| accounts | `tests.py` | 7.2KB |
| courses | `tests.py` | 6.7KB |
| courses | `test_forms.py` | 2.7KB |
| courses | `tests/test_popular_search.py` | 2.9KB |
| courses | `tests/test_webp_compression.py` | 3.9KB |
| api | `tests.py` | 6.7KB |
| api | `test_search.py` | 13.1KB |
| api | `tests/test_tenant_admin_endpoints.py` | 4.1KB |
| payments | `tests.py` | 10.1KB |
| discussions | `tests.py` | 4KB |
| notifications | `tests.py` | 1.6KB |
| analytics | `tests.py` | 2.2KB |

### Running Tests
```bash
pytest
pytest --cov  # With coverage
```

---

## Docker Setup

| File | Mô Tả |
|------|-------|
| `docker/Dockerfile` | Application image |
| `docker/docker-compose.yml` | Development setup |
| `docker/docker-compose.prod.yml` | Production setup |
| `docker/nginx/default.conf` | Nginx configuration |
| `docker/entrypoint.sh` | Container entrypoint |

---

## Known Issues & Technical Debt

1. **Views phân tán**: `apps/courses/includes/` chứa 10+ file views, khó maintain
2. **API views quá lớn**: `apps/api/views.py` (27.8KB) cần tách nhỏ
3. **Lesson model**: Có cả `section` và `subsection` FK (cả hai nullable)
4. **Custom User Model**: Dùng Profile thay vì Custom User từ đầu
5. **Database**: SQLite mặc định, cần PostgreSQL cho production
6. **Cache**: DatabaseCache thay vì Redis
7. **Templates**: Không có app-specific template directories

---

## Conventions

### Code Style
- Black formatting
- isort for imports
- flake8 for linting
- mypy for type checking

### Naming Conventions
- URL names: `snake_case` với `app_name:view_name`
- Models: `PascalCase`
- Functions/Views: `snake_case`

### Git Workflow
- Main branch: `main`
- Feature branches: `feature/xxx`
- Bug fixes: `fix/xxx`
