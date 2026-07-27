from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Cart, CartItem, Products,Category
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer,ProductDetailSerializer,CategoryListSerialzer,CategoryDetailSerialzer
# Create your views here.


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
    



