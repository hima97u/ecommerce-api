[1mdiff --git a/apiApp/signals.py b/apiApp/signals.py[m
[1mindex 87e44c8..0b92d12 100644[m
[1m--- a/apiApp/signals.py[m
[1m+++ b/apiApp/signals.py[m
[36m@@ -1,8 +1,31 @@[m
[31m-from django.db.models.signals import post_save, post_delete [m
[32m+[m[32mfrom django.core.cache import cache[m
[32m+[m[32mfrom django.db.models.signals import post_save, post_delete[m
 from django.dispatch import receiver[m
 from django.db.models import Avg[m
 [m
[31m-from apiApp.models import ProductRating, Review[m
[32m+[m[32mfrom apiApp.models import Category, ProductRating, Products, Review[m
[32m+[m
[32m+[m
[32m+[m[32mdef invalidate_catalog_cache(instance):[m
[32m+[m[32m    keys = [[m
[32m+[m[32m        "products:list",[m
[32m+[m[32m        "categories:list",[m
[32m+[m[32m        f"product:{instance.pk}",[m
[32m+[m[32m        f"product:{getattr(instance, 'slug', '')}",[m
[32m+[m[32m        f"category:{instance.pk}",[m
[32m+[m[32m        f"category:{getattr(instance, 'slug', '')}",[m
[32m+[m[32m    ][m
[32m+[m[32m    cache.delete_many([key for key in keys if not key.endswith(":")])[m
[32m+[m
[32m+[m
[32m+[m[32m@receiver([post_save, post_delete], sender=Products)[m
[32m+[m[32mdef invalidate_product_cache(sender, instance, **kwargs):[m
[32m+[m[32m    invalidate_catalog_cache(instance)[m
[32m+[m
[32m+[m
[32m+[m[32m@receiver([post_save, post_delete], sender=Category)[m
[32m+[m[32mdef invalidate_category_cache(sender, instance, **kwargs):[m
[32m+[m[32m    invalidate_catalog_cache(instance)[m
 [m
 [m
 [m
