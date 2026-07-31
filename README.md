<div align="center">

# Ecommerce API

_A production-minded RESTful ecommerce backend built with Django REST Framework, Stripe Checkout, and a clean relational data model._

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
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview

Ecommerce API is a RESTful backend for a modern online store. It is built with Django REST Framework and focuses on core ecommerce workflows: product and category browsing, cart management, order creation, wishlist support, product reviews and ratings, and secure Stripe Checkout payment processing with webhook confirmation.

The codebase is intentionally structured around production-ready backend concerns: a custom user model, relational data integrity, serializer-driven API responses, media handling, and payment verification through Stripe webhooks.

Note: the repository currently ships with SQLite for local development, while PostgreSQL is the recommended production database.

## Features

- ✓ Custom user model with JWT-ready authentication architecture
- ✓ User registration and login-ready backend foundation
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
- ✓ Secure, serializer-driven request and response handling

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python |
| Framework | Django |
| API Layer | Django REST Framework |
| Database | PostgreSQL |
| Payments | Stripe Checkout + Webhooks |
| Authentication | JWT / Simple JWT friendly architecture |
| Application Server | Gunicorn |
| Reverse Proxy | Nginx |
| Async / Cache Ready | Redis, Celery (optional) |
| Local Media | Django media files |
| Env Management | python-dotenv |

## Architecture

The API follows a standard request pipeline:

```mermaid
flowchart TD
    A[Client] --> B[Django URLs]
    B --> C[Views]
    C --> D[Serializers]
    D --> E[Models]
    E --> F[(PostgreSQL)]
```

Each incoming request is routed through Django URLs, handled by function-based DRF views, validated and shaped by serializers, persisted through Django models, and stored in the database.

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

### 2. Create a virtual environment

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
| `DATABASE_URL` | PostgreSQL database URL | `postgres://user:pass@localhost:5432/ecommerce` |
| `STRIPE_SECRET_KEY` | Stripe secret API key | `sk_test_...` |
| `STRIPE_PUBLIC_KEY` | Stripe public API key | `pk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

Example `.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/ecommerce
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_public_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/product_list` | List featured products |
| `GET` | `/products/<slug>` | Retrieve a single product by slug |
| `GET` | `/category_list` | List all categories |
| `GET` | `/category/<slug>/` | Retrieve category details with products |
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

This project is designed around a custom user model and a JWT-friendly API architecture. In a JWT-based flow, the client authenticates once, receives an access token, and sends that token with each protected request.

Sample Authorization header:

```http
Authorization: Bearer <your_access_token>
```

Typical JWT usage looks like this:

1. The user logs in with valid credentials.
2. The server returns an access token and, optionally, a refresh token.
3. The client stores the tokens securely.
4. Subsequent API requests include the bearer token in the `Authorization` header.
5. The backend verifies the token before allowing protected operations.

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

## Deployment

For production, the typical deployment shape is:

- **Gunicorn** as the Python application server
- **Nginx** as the reverse proxy and static/media front door
- **PostgreSQL** as the production database
- **Environment variables** for secrets, database connection details, and Stripe credentials

<details>
<summary>Production notes</summary>

In a hardened setup, collect static assets, serve media safely, and place the app behind Nginx with Gunicorn bound to a Unix socket or local TCP port. If you add asynchronous jobs later, Redis and Celery fit naturally for email delivery, caching, background sync, and long-running tasks.

</details>

## Future Improvements

- Wishlist enhancements and curated saved lists
- Coupon and discount engine
- Inventory tracking and stock reservation
- Email notifications for orders and account events
- Docker-based local and production environments
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

**GitHub:** [your-github-username](https://github.com/hima97u)

**LinkedIn:** [your-linkedin-profile](https://linkedin.com/in/hima97u)
