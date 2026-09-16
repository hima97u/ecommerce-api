from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Cart, Order


@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.prefetch_related("items__product").get(pk=order_id)
    currency = order.currency.upper()
    item_lines = []
    subtotal = Decimal("0.00")
    for item in order.items.all():
        line_subtotal = item.product.price * item.quantity
        subtotal += line_subtotal
        item_lines.append(
            f"{item.product.name} | Quantity: {item.quantity} | "
            f"Unit price: {currency} {item.product.price:.2f} | "
            f"Subtotal: {currency} {line_subtotal:.2f}"
        )

    total = order.amount / Decimal("100")
    message = "\n".join([
        "Order Confirmation",
        "",
        f"Order ID: #{order.stripe_checkout_id}",
        f"Customer email: {order.customer_email}",
        f"Order date: {order.created_at:%Y-%m-%d %H:%M UTC}",
        f"Payment status: {order.status}",
        "",
        "Products:",
        *item_lines,
        "",
        f"Subtotal: {currency} {subtotal:.2f}",
        f"Order total: {currency} {total:.2f}",
    ])
    send_mail(
        subject=f"Order confirmation: {order.stripe_checkout_id}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        fail_silently=False,
    )
    return order_id


@shared_task
def cleanup_abandoned_carts():
    cutoff = timezone.now() - timedelta(days=30)
    carts = Cart.objects.filter(updated_at__lt=cutoff, cartitems__isnull=True)
    deleted_count, _ = carts.delete()
    return deleted_count
