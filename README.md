<div align="center">

# Ecommerce API

_A local-development RESTful ecommerce backend built with Django REST Framework, Stripe Checkout, and a clean relational data model._

<p>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-REST%20API-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/DRF-API%20Framework-ff1709?style=for-the-badge&logo=django&logoColor=white" alt="Django REST Framework" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe&logoColor=white" alt="Stripe" />
</p>

<p>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/github/stars/OWNER/REPO?style=flat-square" alt="GitHub Stars" />
  <img src="https://img.shields.io/github/last-commit/OWNER/REPO?style=flat-square" alt="Last Commit" />
  <img src="https://img.shields.io/github/repo-size/OWNER/REPO?style=flat-square" alt="Repo Size" />
</p>

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Stripe Integration](#stripe-integration)
- [Example Request](#example-request)
- [Example Response](#example-response)
- [Error Responses](#error-responses)
- [Security](#security)
- [Screenshots](#screenshots)
- [Local Docker Setup](#local-docker-setup)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview

Ecommerce API is a RESTful backend for a modern online store. It is built with Django REST Framework and focuses on core ecommerce workflows: product and category browsing, cart management, order creation, wishlist support, product reviews and ratings, and secure Stripe Checkout payment processing with webhook confirmation.

The local development stack uses Docker Compose with Django's development server behind Nginx, PostgreSQL for persistence, Redis for public catalog caching and Celery broker traffic, and Celery Beat for periodic jobs. Secrets are supplied through environment variables.

This project is for local development and testing only. It does not include production deployment infrastructure.

## Features

- ✓ Custom user model with JWT authentication
- ✓ Role-based authorization through authenticated users and staff administrators
- ✓ Product CRUD and detailed product views
- ✓ Category CRUD and category-based browsing
- ✓ Product search across names, descriptions, and categories
- ✓ Shopping cart and cart item management
- ✓ Order creation from Stripe checkout events
- ✓ Stripe Checkout Session generation
- ✓ Stripe webhook signature verification
- ✓ Reviews and ratings with unique per-user review rules
- ✓ Wishlist add/remove behavior
- ✓ Pagination-ready REST architecture
- ✓ Validation-focused API design
- ✓ Admin panel for internal management
- ✓ Redis caching for public product and category reads
- ✓ Celery worker and Celery Beat for background and scheduled jobs
- ✓ Local Docker Compose setup with PostgreSQL, Redis, and Nginx
- ✓ Application and container health checks
- ✓ Secure, serializer-driven request and response handling

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python |
| Framework | Django |
| API Layer | Django REST Framework |
| Database | PostgreSQL (Docker) |
| Payments | Stripe Checkout + Webhooks |
| Authentication | Django REST Framework Simple JWT |
| Application Server | Django development server (`runserver`) |
| Reverse Proxy | Nginx (local Docker proxy) |
| Cache / Broker | Redis |
| Background Jobs | Celery Worker and Celery Beat |
| Local Media | Django media files |
| Env Management | python-dotenv |

## Architecture

The API follows a standard request pipeline:

```mermaid
flowchart TD
  A[Browser or API Client] --> B[Nginx]
  B --> C[Django runserver :8000]
  C --> D[Views and Serializers]
  D --> E[(PostgreSQL)]
  C --> F[(Redis Cache)]
  F --> G[Celery Worker]
  G --> H[Celery Beat Jobs]
```

Nginx is the local entry point and proxies requests to Django's development server. Django uses PostgreSQL for application data and Redis for public catalog caching and Celery broker traffic. User-specific data is not globally cached.

### Stripe payment flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Stripe
    participant W as Webhook
    participant DB as Database

    C->>A: POST /create_checkout_session/ with cart_code + email
    A->>S: Create Stripe Checkout Session
    S-->>C: Redirect to hosted checkout page
    C->>S: Complete payment
    S-->>W: checkout.session.completed webhook
    W->>A: Verify Stripe signature
    A->>DB: Create Order + OrderItem records
    A->>DB: Delete fulfilled cart
```

The webhook is the source of truth for payment completion. Checkout success alone does not create an order; the signed Stripe event does.

## Database Schema

The domain model is centered around a custom user, catalog data, shopping state, and post-payment fulfillment.

- **User** - Custom Django user model with email uniqueness and profile picture support.
- **Product** - Product catalog entry with name, description, price, slug, image, and featured flag.
- **Category** - Product grouping with slug and optional image.
- **Cart** - Temporary shopping session identified by a cart code.
- **CartItem** - Line item linking a cart to a product and quantity.
- **Order** - Stripe-backed payment record containing checkout ID, amount, currency, customer email, and status.
- **OrderItem** - Individual purchased items attached to an order.
- **Review** - Product review with rating and review text; one review per user per product.
- **Rating** - Aggregated product rating record with average score and review count.

## Folder Structure

```text
ecommerce_api/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── nginx/
│   └── nginx.conf
├── apiApp/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
└── ecommerceApiProject/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## Installation

Follow the steps below to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/OWNER/REPO.git
cd REPO
```

### Docker Compose (recommended)

Copy the example environment file and set local values:

```bash
cp .env.example .env
docker compose up --build
```

The primary local URL is `http://localhost/` through Nginx. Django is also published at `http://localhost:8000/` for debugging.

Run migrations and create an administrator:

```bash
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
```

Inspect background-job logs:

```bash
docker compose logs -f celery_worker
docker compose logs -f celery_beat
```

Stop the stack with `docker compose down`.

### Running without Docker

Create a virtual environment:

```bash
python -m venv ecommerceEnv
```

### 3. Activate the environment

Windows:

```bash
ecommerceEnv\Scripts\activate
```

macOS / Linux:

```bash
source ecommerceEnv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and add the variables listed below.

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Enable debug mode | `True` |
| `POSTGRES_DB` | PostgreSQL database name | `ecommerce` |
| `POSTGRES_USER` | PostgreSQL username | `ecommerce` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `change-me-locally` |
| `POSTGRES_HOST` | PostgreSQL Compose service name | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Redis cache URL | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://redis:6379/1` |
| `STRIPE_SECRET_KEY` | Stripe secret API key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `EMAIL_HOST` | SMTP host; console backend is the default | `localhost` |
| `EMAIL_PORT` | SMTP port | `1025` |
| `EMAIL_HOST_USER` | SMTP username | `` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

Example `.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
POSTGRES_DB=ecommerce
POSTGRES_USER=ecommerce
POSTGRES_PASSWORD=change-me-locally
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/product_list` | List featured products |
| `GET` | `/products/<slug>` | Retrieve a single product by slug |
| `GET` | `/category_list` | List all categories |
| `GET` | `/category/<slug>/` | Retrieve category details with products |
| `GET` | `/api/health/` | Return application health |
| `POST` | `/api/auth/token/` | Obtain JWT access and refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh a JWT access token |
| `POST` | `/api/auth/token/verify/` | Verify a JWT access token |
| `POST` | `/add_to_cart/` | Create or update a cart with a product |
| `PUT` | `/update_cartitem_quantity/` | Update cart item quantity |
| `DELETE` | `/delete_cartitem/<int:pk>/` | Delete a cart item |
| `POST` | `/add_review/` | Create a review for a product |
| `PUT` | `/update_review/<int:pk>/` | Update an existing review |
| `DELETE` | `/delete_review/<int:pk>/` | Delete a review |
| `POST` | `/add_to_wishlist/` | Add or remove a product from wishlist |
| `GET` | `/search?query=...` | Search products by keyword |
| `POST` | `/create_checkout_session/` | Create a Stripe Checkout Session |
| `POST` | `/webhook/` | Receive Stripe webhook events |
| `GET` | `/admin/` | Django admin panel |

## Authentication

Protected cart, review, wishlist, checkout, and order operations use Django REST Framework Simple JWT. Users may access only their own private resources. Staff administrators continue to use Django admin for product, category, and order management.

Sample Authorization header:

```http
Authorization: Bearer <your_access_token>
```

Typical JWT usage looks like this:

1. The user posts credentials to `/api/auth/token/`.
2. The server returns an access token and a refresh token.
3. The client stores the tokens securely.
4. Subsequent API requests include the bearer token in the `Authorization` header.
5. The backend verifies the token before allowing protected operations.

```http
POST /api/auth/token/
Content-Type: application/json

{"username": "customer", "password": "your-password"}
```

Send the returned access token with `Authorization: Bearer <access_token>`.

## Caching and Background Jobs

Public product and category list/detail responses use Redis with a 5-minute TTL. Catalog writes invalidate related public keys. Cart, order, wishlist, and profile data is user-specific and is not shared through the public cache.

Celery uses Redis as its broker and result backend. Paid orders queue a confirmation email task after Stripe fulfillment. Celery Beat schedules conservative cleanup of old empty carts; it does not delete carts containing customer items or order data.

## Stripe Integration

Stripe powers the checkout and payment confirmation flow.

1. **Create Checkout Session** - The client posts a `cart_code` and `email` to `/create_checkout_session/`.
2. **Redirect** - The API returns a Stripe Checkout Session payload and the client redirects the buyer to Stripe-hosted checkout.
3. **Payment** - Stripe handles the payment UI and card processing.
4. **Webhook** - Stripe sends a signed webhook event to `/webhook/` after payment succeeds.
5. **Order Update** - The webhook handler verifies the Stripe signature, creates the `Order` and `OrderItem` records, and removes the fulfilled cart.

## Example Request

```json
{
  "cart_code": "CART12345",
  "email": "customer@example.com"
}
```

Example request to create a checkout session:

```http
POST /create_checkout_session/
Content-Type: application/json

{
  "cart_code": "CART12345",
  "email": "customer@example.com"
}
```

## Example Response

```json
{
  "data": {
    "id": "cs_test_123456789",
    "object": "checkout.session",
    "amount_total": 2599,
    "currency": "usd",
    "customer_email": "customer@example.com",
    "metadata": {
      "cart_code": "CART12345"
    },
    "url": "https://checkout.stripe.com/c/pay/cs_test_123456789"
  }
}
```

## Error Responses

| Status Code | Meaning | Common Cause |
| --- | --- | --- |
| `200` | OK | Successful fetch, update, or webhook confirmation |
| `201` | Created | New resource created successfully |
| `204` | No Content | Resource deleted successfully |
| `400` | Bad Request | Missing data, invalid payload, Stripe verification failure |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | User lacks permission to access the resource |
| `404` | Not Found | Product, cart item, order, or category does not exist |
| `500` | Internal Server Error | Unhandled server-side exception |

## Security

- JWT-based authentication is the recommended access control layer for protected endpoints.
- CSRF protection is enabled for normal Django requests, while the Stripe webhook is explicitly exempted because Stripe signs the payload instead.
- Request data is validated through DRF serializers and view-level checks.
- Permissions should be enforced for sensitive operations such as order management, review updates, and account-specific resources.
- Stripe webhook requests are verified using the signed event header before any order is created.

## Screenshots

Add your project screenshots here to make the README feel complete and recruiter-ready.

<details>
<summary>Open screenshot placeholders</summary>

### Swagger

![Swagger UI](docs/screenshots/swagger.png)

### Postman

![Postman Collection](docs/screenshots/postman.png)

### Admin Panel

![Admin Panel](docs/screenshots/admin-panel.png)

### Stripe Checkout

![Stripe Checkout](docs/screenshots/stripe-checkout.png)

</details>

## Local Docker Setup

Docker Compose provides these local services:

| Service | Purpose |
| --- | --- |
| `django` | Runs `python manage.py runserver 0.0.0.0:8000` |
| `postgres` | PostgreSQL database |
| `redis` | Cache and Celery broker/backend |
| `celery_worker` | Executes asynchronous tasks |
| `celery_beat` | Schedules periodic Celery tasks |
| `nginx` | Local reverse proxy at `http://localhost/` |

Containers communicate through Compose service names: Django uses `postgres` and `redis`, Celery uses `redis`, and Nginx proxies to `django:8000`. This stack is for local development/testing only and does not include deployment infrastructure.

## Future Improvements

- Wishlist enhancements and curated saved lists
- Coupon and discount engine
- Inventory tracking and stock reservation
- Email notifications for orders and account events
- Docker-based local development environment
- Redis caching for hot catalog reads
- Celery for background jobs and webhook follow-up work
- Search indexing with Elasticsearch

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make your changes with clear, focused commits.
4. Add or update tests where relevant.
5. Ensure migrations, formatting, and API behavior still pass locally.
6. Open a pull request with a concise summary of the change and any relevant screenshots or sample requests.

Suggested pull request expectations:

- Keep changes scoped to a single concern.
- Document API changes in the README or a dedicated changelog note.
- Avoid breaking existing endpoint contracts unless the change is explicitly versioned.

## License

This project is licensed under the MIT License.

## Author

**GitHub:** [GitHub](https://github.com/hima97u)

**LinkedIn:** [Linkedin](https://linkedin.com/in/hima97u)
