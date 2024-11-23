from django.core.management.base import BaseCommand
from store.models import Category

class Command(BaseCommand):
    help = 'Sets up main categories and their subcategories'

    def handle(self, *args, **kwargs):
        # Define categories and their subcategories
        category_structure = {
            'Electronics': ['Laptops', 'Smartphones', 'Tablets', 'Accessories'],
            'Clothing': ['Men', 'Women', 'Children', 'Sports'],
            'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Garden'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics']
        }

        for main_category, subcategories in category_structure.items():
            # Create main category
            main_cat, _ = Category.objects.get_or_create(
                name=main_category,
                defaults={'is_department': True}
            )
            
            # Create subcategories
            for subcat in subcategories:
                Category.objects.get_or_create(
                    name=subcat,
                    defaults={'parent': main_cat, 'is_department': False}
                )

        self.stdout.write(self.style.SUCCESS('Categories setup completed')) 