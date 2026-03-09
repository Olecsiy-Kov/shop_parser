import time

from django.core.management.base import BaseCommand
from products.models import Product
from products.services.brain_parser import get_catalog_product_urls, parse_brain_product


class Command(BaseCommand):
    help = "Parse all iPhones from brain.com.ua catalog"

    def save_product(self, data):
        product, created = Product.objects.update_or_create(
            product_code=data["product_code"],
            defaults={
                "name": data["name"] or "",
                "url": data["url"],
                "manufacturer": data["manufacturer"],
                "color": data["color"],
                "memory": data["memory"],
                "screen_size": data["screen_size"],
                "resolution": data["resolution"],
                "price_regular": data["price_regular"],
                "price_current": data["price_current"],
                "reviews_count": data["reviews_count"],
                "images": data["images"][:5],
                "characteristics": data["characteristics"],
            },
        )
        return product, created

    def handle(self, *args, **options):
        catalog_url = "https://brain.com.ua/ukr/category/Telefony_mobilni-c1274/filter=3-83017200000/"

        product_urls = get_catalog_product_urls(catalog_url, max_pages=20)
        self.stdout.write(f"CATALOG URLS FOUND: {len(product_urls)}")

        queue = list(product_urls)
        processed = set()
        discovered = set(product_urls)
        failed_urls = []

        while queue:
            url = queue.pop(0)

            if url in processed:
                continue

            processed.add(url)

            try:
                data = parse_brain_product(url)
                product, created = self.save_product(data)

                self.stdout.write(
                    f"{'Created' if created else 'Updated'}: {product.name}"
                )

                for variant_url in data.get("variant_urls", []):
                    if variant_url not in discovered and variant_url not in processed:
                        discovered.add(variant_url)
                        queue.append(variant_url)

                time.sleep(2)

            except Exception as e:
                failed_urls.append(url)
                self.stdout.write(self.style.ERROR(f"Error: {url} -> {e}"))
                time.sleep(3)

        if failed_urls:
            self.stdout.write(self.style.WARNING(f"RETRY FAILED URLS: {len(failed_urls)}"))

            for url in failed_urls[:]:
                try:
                    data = parse_brain_product(url)
                    product, created = self.save_product(data)

                    self.stdout.write(
                        f"RETRY {'Created' if created else 'Updated'}: {product.name}"
                    )
                    time.sleep(2)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"RETRY Error: {url} -> {e}"))

        self.stdout.write(self.style.SUCCESS(f"TOTAL PROCESSED: {len(processed)}"))