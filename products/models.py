from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=500)
    url = models.URLField(unique=True)

    product_code = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=200, blank=True, null=True)
    memory = models.CharField(max_length=200, blank=True, null=True)
    screen_size = models.CharField(max_length=100, blank=True, null=True)
    resolution = models.CharField(max_length=100, blank=True, null=True)

    price_regular = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_current = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    reviews_count = models.PositiveIntegerField(default=0)

    characteristics = models.JSONField(default=dict, blank=True)
    images = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name
