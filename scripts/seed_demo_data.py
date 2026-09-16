import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerceApiProject.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache

from apiApp.models import Cart, CartItem, Category, Products


User = get_user_model()


def seed_user(username, email, password, *, is_staff=False, is_superuser=False):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )
    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.set_password(password)
    user.save()
    return user


def seed_product(name, description, price, category, *, featured=True):
    product, _ = Products.objects.get_or_create(
        slug=name.lower().replace(" ", "-"),
        defaults={
            "name": name,
            "description": description,
            "price": price,
            "Category": category,
            "featured": featured,
        },
    )
    product.name = name
    product.description = description
    product.price = price
    product.Category = category
    product.featured = featured
    product.save()
    return product


def main():
    admin = seed_user(
        "demo-admin",
        "admin@example.local",
        "AdminPass123!",
        is_staff=True,
        is_superuser=True,
    )
    customer = seed_user(
        "demo-customer",
        "customer@example.local",
        "CustomerPass123!",
    )

    keyboards, _ = Category.objects.get_or_create(
        slug="keyboards",
        defaults={"name": "Keyboards"},
    )
    mice, _ = Category.objects.get_or_create(
        slug="mice",
        defaults={"name": "Mice"},
    )

    mechanical_keyboard = seed_product(
        "Mechanical Keyboard",
        "Hot-swappable mechanical keyboard with RGB lighting.",
        "75.00",
        keyboards,
    )
    wireless_mouse = seed_product(
        "Wireless Mouse",
        "Ergonomic wireless mouse with adjustable DPI.",
        "25.00",
        mice,
    )
    desk_mat = seed_product(
        "Desk Mat",
        "Large water-resistant desk mat.",
        "20.00",
        mice,
    )

    cart, _ = Cart.objects.get_or_create(
        cart_code="demo-cart",
        defaults={"user": customer},
    )
    if cart.user_id != customer.id:
        cart.user = customer
        cart.save(update_fields=["user"])

    for product, quantity in (
        (mechanical_keyboard, 2),
        (wireless_mouse, 1),
        (desk_mat, 1),
    ):
        CartItem.objects.update_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

    cache.clear()

    print("Demo data created or updated.")
    print(f"Admin login: demo-admin / AdminPass123! ({admin.email})")
    print(f"Customer login: demo-customer / CustomerPass123! ({customer.email})")
    print(f"Cart code: {cart.cart_code}")
    print("Products:")
    for product in (mechanical_keyboard, wireless_mouse, desk_mat):
        print(f"  id={product.id} slug={product.slug} price={product.price}")
    print("Cart contents: 2 x Mechanical Keyboard, 1 x Wireless Mouse, 1 x Desk Mat")


if __name__ == "__main__":
    main()
