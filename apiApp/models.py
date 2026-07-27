from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True , null=True)

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=25)
    slug = models.SlugField(unique=True,blank=True)
    image = models.ImageField(upload_to="category_img",blank=True,null=True)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Products.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug

        super().save(*args,**kwargs)



class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    slug = models.SlugField(unique=True,blank=True)
    image = models.ImageField(upload_to="product_img",blank=True,null=True)
    featured = models.BooleanField(default=False)
    Category = models.ForeignKey(Category,on_delete=models.SET_NULL,related_name="products",blank=True,null=True)

    def __str__(self):
        return self.name


    def save(self,*args,**kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Products.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug

        super().save(*args,**kwargs)


class Cart(models.Model):
    cart_code = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cartitems")
    product =  models.ForeignKey(Products,on_delete=models.CASCADE,related_name="item")
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} X {self.product.name} in cart {self.cart.id}"

