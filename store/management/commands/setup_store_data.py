from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Sets up categories and test products'

    def handle(self, *args, **kwargs):
        # First, create categories
        category_structure = {
            'Electronics': ['Laptops', 'Smartphones', 'Tablets', 'Accessories'],
            'Clothing': ['Men', 'Women', 'Children', 'Sports'],
            'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Garden'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics']
        }

        # Create categories
        for dept_name, subcats in category_structure.items():
            # Create department
            dept, _ = Category.objects.get_or_create(
                name=dept_name,
                defaults={
                    'slug': slugify(dept_name),
                    'is_department': True
                }
            )
            self.stdout.write(f'Created department: {dept_name}')

            # Create subcategories
            for subcat_name in subcats:
                subcat, _ = Category.objects.get_or_create(
                    name=subcat_name,
                    defaults={
                        'slug': slugify(subcat_name),
                        'parent': dept,
                        'is_department': False
                    }
                )
                self.stdout.write(f'Created subcategory: {subcat_name} under {dept_name}')

        # Create test products
        test_products = [
            # Electronics
            {'name': 'Gaming Laptop', 'price': 1299.99, 'category': 'Laptops', 'brand': 'TechPro'},
            {'name': 'Smartphone X', 'price': 699.99, 'category': 'Smartphones', 'brand': 'TechPro'},
            {'name': 'Tablet Pro', 'price': 499.99, 'category': 'Tablets', 'brand': 'TechPro'},
            
            # Clothing
            {'name': 'Men\'s Jacket', 'price': 89.99, 'category': 'Men', 'brand': 'FashionCo'},
            {'name': 'Women\'s Dress', 'price': 69.99, 'category': 'Women', 'brand': 'FashionCo'},
            {'name': 'Kids T-Shirt', 'price': 19.99, 'category': 'Children', 'brand': 'FashionCo'},
            
            # Home & Garden
            {'name': 'Sofa Set', 'price': 899.99, 'category': 'Furniture', 'brand': 'HomePlus'},
            {'name': 'Wall Art', 'price': 49.99, 'category': 'Decor', 'brand': 'HomePlus'},
            
            # Books
            {'name': 'Mystery Novel', 'price': 14.99, 'category': 'Fiction', 'brand': 'BookCo'},
            {'name': 'Science Book', 'price': 24.99, 'category': 'Educational', 'brand': 'BookCo'},
        ]

        for product_data in test_products:
            try:
                category = Category.objects.get(name=product_data['category'])
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'price': product_data['price'],
                        'category': category,
                        'brand': product_data['brand'],
                        'description': f"This is a test {product_data['name']}",
                        'is_available': True,
                        'stock': 10
                    }
                )
                if created:
                    self.stdout.write(f'Created product: {product_data["name"]}')
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Category {product_data["category"]} not found')
                )

        self.stdout.write(self.style.SUCCESS('Successfully set up store data')) 