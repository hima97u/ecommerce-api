from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Products,Category
from .serializers import ProductListSerializer,ProductDetailSerializer,CategoryListSerialzer,CategoryDetailSerialzer
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
