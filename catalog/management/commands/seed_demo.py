from decimal import Decimal
from django.core.management.base import BaseCommand
from catalog.models import Category, Product

CATEGORIES = [
    ("electronics", "Electronics"), ("phones", "Phones"), ("computers", "Computers"),
    ("clothing", "Clothing"), ("shoes", "Shoes"), ("accessories", "Accessories"),
    ("home-living", "Home & Living"),
]

# (name, category slug, current price, original price or None, stock, image seed)
PRODUCTS = [
    ("Nike Air Max 90", "shoes", 8500, 10000, 15, "soko-shoe1"),
    ("Samsung Galaxy A15", "phones", 18999, None, 8, "soko-phone1"),
    ("HP Pavilion 15 Laptop", "computers", 62000, 71500, 4, "soko-laptop1"),
    ("JBL Tune 510BT Headphones", "electronics", 4200, 5000, 22, "soko-headphones1"),
    ("Ankara Print Shirt", "clothing", 1800, None, 30, "soko-shirt1"),
    ("Leather Crossbody Bag", "accessories", 3200, 4000, 0, "soko-bag1"),
    ("Non-Stick Cookware Set (6pc)", "home-living", 5600, None, 12, "soko-cookware1"),
    ("iPhone 13 (Refurbished)", "phones", 54000, 62000, 3, "soko-phone2"),
    ("Adidas Runfalcon Sneakers", "shoes", 5400, None, 18, "soko-shoe2"),
    ("Wireless Mouse & Keyboard Combo", "computers", 2100, 2600, 25, "soko-combo1"),
    ("Smart LED Bulb (4-Pack)", "home-living", 3400, None, 9, "soko-bulb1"),
    ("Denim Jacket", "clothing", 3900, 4800, 14, "soko-jacket1"),
    ("Fitness Tracker Watch", "electronics", 3800, None, 0, "soko-watch1"),
    ("Aviator Sunglasses", "accessories", 1500, 1900, 40, "soko-glasses1"),
    ("Tecno Spark 10", "phones", 15500, None, 11, "soko-phone3"),
    ("Office Desk Lamp", "home-living", 1650, None, 20, "soko-lamp1"),
]


class Command(BaseCommand):
    help = "Load demo categories and products (safe to run more than once)."

    def handle(self, *args, **options):
        cats = {}
        for slug, name in CATEGORIES:
            cats[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})

        for name, slug, current, original, stock, img in PRODUCTS:
            # Model convention: price = normal price, discount_price = what's charged on sale.
            price = Decimal(original) if original else Decimal(current)
            discount = Decimal(current) if original else None
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": cats[slug],
                    "price": price,
                    "discount_price": discount,
                    "stock": stock,
                    "image": f"https://picsum.photos/seed/{img}/500/500",
                    "description": f"{name} — demo product.",
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products."))
