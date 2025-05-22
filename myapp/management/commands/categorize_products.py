# # filepath: /Users/lovepreetsahota/Desktop/FinalPP/myapp/management/commands/categorize_products.py

# from django.core.management.base import BaseCommand
# from myapp.models import Products


# # Brooks Brothers-style categories and their keywords
# CATEGORY_KEYWORDS = {
#     "Men's Dress Shirts": ["regent", "madison", "dress shirt", "oxford shirt"],
#     "Men's Casual Shirts": ["sport shirt", "casual shirt", "button-down", "plaid shirt", "friday", "poplin"],
#     "Men's Polos & Tees": ["Polo", "t-shirt", "tee"],
#     "Men's Trousers & Shorts": ["trousers", "chino", "shorts", "pants", "khaki", "cargo", "boxers"],
#     "Men's Suits & Blazers": ["suit", "blazer", "jacket", "sport coat", "harington", "vest","windowpane"],
#     "Men's Accessories": ["tie", "belt", "wallet", "scarf", "cufflink", "hat", "socks"],
#     "Women's Shirts & Blouses": ["blouse", "shirt", "oxford", "tunic", "sweater"],
#     "Women's Dresses & Skirts": ["dress", "shirtdress", "sheath", "skirt", "utility dress", "midi dress"],
#     "Women's Pants": ["pant", "trouser", "legging"],
#     "Women's Accessories": ["scarf", "bag", "belt", "jewelry"],
#     "Outerwear": ["coat", "jacket", "parka", "trench", "overcoat", "windbreaker"],
#     "Sleepwear & Loungewear": ["pajama", "robe", "sleep", "lounge"],
#     "Footwear": ["loafer", "sneaker", "oxford", "boot", "brogue", "pump", "flat"],
# }

# # Map category names to gender
# CATEGORY_TO_GENDER = {
#     cat: "Men" for cat in CATEGORY_KEYWORDS if cat.startswith("Men's")
# } | {
#     cat: "Women" for cat in CATEGORY_KEYWORDS if cat.startswith("Women's")
# } | {
#     "Outerwear": "Unisex",
#     "Sleepwear & Loungewear": "Unisex",
#     "Footwear": "Unisex"
# }

# class Command(BaseCommand):
#     help = "Categorize Brooks Brothers products and assign gender based on categories"

#     def handle(self, *args, **kwargs):
#         products = Products.objects.all()
#         updated_count = 0

#         for product in products:
#             name = (product.name or "").lower()
#             category_found = False

#             # Assign category based on keywords
#             for category, keywords in CATEGORY_KEYWORDS.items():
#                 if any(keyword in name for keyword in keywords):
#                     product.category = category
#                     category_found = True
#                     break

#             if not category_found:
#                 product.category = "Uncategorized"

#             # Assign gender from category
#             product.details = CATEGORY_TO_GENDER.get(product.category, "Unisex")

#             product.save()
#             updated_count += 1

#         self.stdout.write(
#             self.style.SUCCESS(f"{updated_count} products categorized and gender assigned.")
#         )