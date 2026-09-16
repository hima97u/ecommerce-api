from django.core.cache import cache
from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Cart, CartItem, CustomUser, Order, OrderItem, Products
from .tasks import send_order_confirmation_email


class EcommerceApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = CustomUser.objects.create_user(
			username="user-one",
			email="one@example.com",
			password="Strong-password-123",
		)
		self.other_user = CustomUser.objects.create_user(
			username="user-two",
			email="two@example.com",
			password="Strong-password-123",
		)
		self.product = Products.objects.create(
			name="Test product",
			description="A test product",
			price="10.00",
			featured=True,
		)
		cache.clear()

	def authenticate(self, user):
		response = self.client.post(
			"/api/auth/token/",
			{"username": user.username, "password": "Strong-password-123"},
			format="json",
		)
		self.assertEqual(response.status_code, 200)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

	def test_jwt_login_and_health_endpoint(self):
		response = self.client.get("/api/health/")
		self.assertEqual(response.data, {"status": "healthy"})

		self.authenticate(self.user)
		response = self.client.get("/orders/")
		self.assertEqual(response.status_code, 200)

	def test_private_cart_requires_jwt(self):
		response = self.client.post(
			"/add_to_cart/",
			{"cart_code": "cart-one", "product_id": self.product.id},
			format="json",
		)
		self.assertEqual(response.status_code, 401)

	def test_invalid_jwt_is_rejected(self):
		self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
		response = self.client.get("/orders/")
		self.assertEqual(response.status_code, 401)

	def test_cart_cannot_be_modified_by_another_user(self):
		self.authenticate(self.user)
		response = self.client.post(
			"/add_to_cart/",
			{"cart_code": "cart-one", "product_id": self.product.id},
			format="json",
		)
		self.assertEqual(response.status_code, 200)
		item = CartItem.objects.get(cart__user=self.user)

		self.authenticate(self.other_user)
		response = self.client.put(
			"/update_cartitem_quantity/",
			{"item_id": item.id, "quantity": 2},
			format="json",
		)
		self.assertEqual(response.status_code, 404)

	def test_product_list_populates_cache(self):
		response = self.client.get("/product_list")
		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(cache.get("products:list"))

	def test_order_confirmation_email_contains_persisted_order_details(self):
		second_product = Products.objects.create(
			name="Mechanical Keyboard",
			description="A mechanical keyboard",
			price="75.00",
		)
		order = Order.objects.create(
			stripe_checkout_id="cs_test_email_details",
			user=self.user,
			amount="17500",
			currency="usd",
			customer_email=self.user.email,
			status="Paid",
		)
		OrderItem.objects.create(order=order, product=self.product, quantity=2)
		OrderItem.objects.create(order=order, product=second_product, quantity=1)

		send_order_confirmation_email(order.pk)

		self.assertEqual(len(mail.outbox), 1)
		message = mail.outbox[0].body
		self.assertIn("Order ID: #cs_test_email_details", message)
		self.assertIn("Customer email: one@example.com", message)
		self.assertIn("Test product | Quantity: 2 | Unit price: USD 10.00 | Subtotal: USD 20.00", message)
		self.assertIn("Mechanical Keyboard | Quantity: 1 | Unit price: USD 75.00 | Subtotal: USD 75.00", message)
		self.assertIn("Subtotal: USD 95.00", message)
		self.assertIn("Order total: USD 175.00", message)
