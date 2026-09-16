import stripe
import logging
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q
from .models import Cart, CartItem, Order, OrderItem, Products,Category, Review, Wishlist
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer,ProductDetailSerializer,CategoryListSerialzer,CategoryDetailSerialzer, ReviewSerializer, WishlistSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_order_confirmation_email
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET
User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['GET'])
def product_list(request):
    cached = cache.get("products:list")
    if cached is not None:
        return Response(cached)
    products = Products.objects.filter(featured=True)
    serializer = ProductListSerializer(products,many=True)
    cache.set("products:list", serializer.data, 300)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request,slug):
    cache_key = f"product:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    product = get_object_or_404(Products, slug=slug)
    serializer = ProductDetailSerializer(product)
    cache.set(cache_key, serializer.data, 300)
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    cached = cache.get("categories:list")
    if cached is not None:
        return Response(cached)
    categories = Category.objects.all()
    serialzer = CategoryListSerialzer(categories,many=True)
    cache.set("categories:list", serialzer.data, 300)
    return Response(serialzer.data)

@api_view(['GET'])
def category_detail(request,slug):
    cache_key = f"category:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    category = get_object_or_404(Category, slug=slug)
    serializer = CategoryDetailSerialzer([category], many=True)
    cache.set(cache_key, serializer.data, 300)
    return Response(serializer.data)


@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")

    cart = Cart.objects.filter(cart_code=cart_code).first()
    if cart and cart.user_id not in (None, request.user.id):
        return Response({"detail": "This cart belongs to another user."}, status=403)
    if cart is None:
        cart = Cart.objects.create(cart_code=cart_code, user=request.user)
    elif cart.user_id is None:
        cart.user = request.user
        cart.save(update_fields=["user"])
    product = get_object_or_404(Products, id=product_id)

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    cartitem.quantity = 1 
    cartitem.save() 

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    quantity = int(quantity)
    
    cartitem = get_object_or_404(CartItem, id=cartitem_id, cart__user=request.user)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({"data":serializer.data , "message":"cartitem updated successfully !! "})
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request):
    product_id = request.data.get("product_id")
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    product = get_object_or_404(Products, id=product_id)
    user = request.user

    if Review.objects.filter(product=product,user=user).exists():
        return Response("you already dropped a review for this project",status=400)

    review = Review.objects.create(product=product,user=user,rating=rating,review=review_text)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request,pk):
    review = get_object_or_404(Review, id=pk, user=request.user)
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    review.rating = rating
    review.review = review_text
    review.save()
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    review = get_object_or_404(Review, id=pk, user=request.user)
    review.delete()

    return Response("Review deleted successfully!", status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    product_id = request.data.get("product_id")

    user = request.user
    product = get_object_or_404(Products, id=product_id)

    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()

        return Response("Wishlist deleted successfully!", status=204)

    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):
    cartitem = get_object_or_404(CartItem, id=pk, cart__user=request.user)
    cartitem.delete()

    return Response("cartitem deleted successfully!", status=204)


@api_view(['GET'])
def product_search(request):
    query = request.query_params.get("query") 
    if not query:
        return Response("No query provided", status=400)
    
    products = Products.objects.filter(Q(name__icontains=query) | 
                                      Q(description__icontains=query) |
                                       Q(Category__name__icontains=query) )
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    cart = get_object_or_404(Cart, cart_code=cart_code, user=request.user)
    email = request.user.email
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email= email,
            payment_method_types=['card'],


            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100),  # Amount in cents
                    },
                    'quantity': item.quantity,
                }
                for item in cart.cartitems.all()
            ] + [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'VAT Fee'},
                        'unit_amount': 500,  # $5 in cents
                    },
                    'quantity': 1,
                }
            ],


           
            mode='payment',
            # success_url="http://localhost:3000/success",
            # cancel_url="http://localhost:3000/cancel",

            success_url="https://next-shop-self.vercel.app/success",
            cancel_url="https://next-shop-self.vercel.app/failed",
            metadata = {"cart_code": cart_code}
        )
        return Response({'data': checkout_session.to_dict()})
    except Exception as e:
        return Response({'error': str(e)}, status=400)




@csrf_exempt
def my_webhook_view(request):
    if request.method != "POST":
        return HttpResponse("Webhook endpoint", status=405)

    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    if not sig_header:
        return HttpResponse("Missing Stripe signature", status=400)

    payload = request.body

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
        session = event['data']['object']
        cart_code = session["metadata"]["cart_code"]

        fulfill_checkout(session, cart_code)


        return HttpResponse(status=200)



def fulfill_checkout(session, cart_code):
    order = Order.objects.filter(stripe_checkout_id=session["id"]).first()
    if order:
        return order

    cart = Cart.objects.select_related("user").get(cart_code=cart_code)
    order = Order.objects.create(
        user=cart.user,
        stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid",
    )
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product, 
                                             quantity=item.quantity)
    
    cart.delete()
    send_order_confirmation_email.delay(order.pk)
    return order


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return Response([
        {
            "id": order.id,
            "stripe_checkout_id": order.stripe_checkout_id,
            "amount": order.amount,
            "currency": order.currency,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ])
