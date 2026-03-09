from django.core.management.base import BaseCommand
from products.models import Product
from products.services.brain_parser import parse_brain_product


class Command(BaseCommand):
    help = "Parse product from brain.com.ua"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str)

    def handle(self, *args, **options):
        data = parse_brain_product(options["url"])

        product, created = Product.objects.update_or_create(
            url=data["url"],
            defaults={
                "name": data["name"] or "",
                "product_code": data["product_code"],
                "manufacturer": data["manufacturer"],
                "color": data["color"],
                "memory": data["memory"],
                "screen_size": data["screen_size"],
                "resolution": data["resolution"],
                "price_regular": data["price_regular"],
                "price_current": data["price_current"],
                "reviews_count": data["reviews_count"],
                "images": data["images"],
                "characteristics": data["characteristics"],
            },
        )

        self.stdout.write(f"{'Created' if created else 'Updated'}: {product.name}")