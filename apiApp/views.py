from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Cart, CartItem, Products,Category, Review
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer,ProductDetailSerializer,CategoryListSerialzer,CategoryDetailSerialzer, ReviewSerializer
from django.contrib.auth import get_user_model
# Create your views here.

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

