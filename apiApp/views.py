import stripe
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import Cart, CartItem, Order, OrderItem, Products,Category, Review, Wishlist
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer,ProductDetailSerializer,CategoryListSerialzer,CategoryDetailSerialzer, ReviewSerializer, WishlistSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET
User = get_user_model()

@api_view(['GET'])
def product_list(request):
    products = Products.objects.filter(featured=True)
    serializer = ProductListSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request,slug):
    product = Products.objects.get(slug=slug)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serialzer = CategoryListSerialzer(categories,many=True)
    return Response(serialzer.data)

@api_view(['GET'])
def category_detail(request,slug):
    category = Category.objects.filter(slug=slug)
    serializer = CategoryDetailSerialzer(category,many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Products.objects.get(id=product_id)

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    cartitem.quantity = 1 
    cartitem.save() 

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    quantity = int(quantity)
    
    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({"data":serializer.data , "message":"cartitem updated successfully !! "})
    

@api_view(['POST'])
def add_review(request):
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    product = Products.objects.get(id=product_id)
    user = User.objects.get(email=email)

    if Review.objects.filter(product=product,user=user).exists():
        return Response("you already dropped a review for this project",status=400)

    review = Review.objects.create(product=product,user=user,rating=rating,review=review_text)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['PUT'])
def update_review(request,pk):
    review = Review.objects.get(id=pk)
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    review.rating = rating
    review.review = review_text
    review.save()
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_review(request, pk):
    review = Review.objects.get(id=pk) 
    review.delete()

    return Response("Review deleted successfully!", status=204)


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get("email")
    product_id = request.data.get("product_id")

    user = User.objects.get(email=email)
    product = Products.objects.get(id=product_id) 

    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()

        return Response("Wishlist deleted successfully!", status=204)

    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_cart_item(request, pk):
    cartitem = CartItem.objects.get(id=pk) 
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
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    cart = Cart.objects.get(cart_code=cart_code)
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
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            metadata = {"cart_code": cart_code}
        )
        return Response({'data': {'session_id': checkout_session.id, 'url': checkout_session.url}})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
    session = event['data']['object']
    cart_code = session.get("metadata", {}).get("cart_code")

    fulfill_checkout(session, cart_code)


  return HttpResponse(status=200)



def fulfill_checkout(session, cart_code):
    try:
        order = Order.objects.create(
            stripe_checkout_id=session["id"],
            amount=session["amount_total"],
            currency=session["currency"],
            customer_email=session["customer_email"],
            status="Paid",
        )

        cart = Cart.objects.get(cart_code=cart_code)

        for item in cart.cartitems.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )

        cart.delete()

    except Exception as e:
        print("ERROR:", e)
