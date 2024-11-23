from django.core.management.base import BaseCommand
from store.models import Category

class Command(BaseCommand):
    help = 'Sets up the Electronics department and subcategories'

    def handle(self, *args, **kwargs):
        # Create Electronics department
        electronics, _ = Category.objects.get_or_create(
            name='Electronics',
            is_department=True
        )

        # Create subcategories
        subcategories = ['Laptops', 'Smartphones', 'Tablets']
        for subcat in subcategories:
            Category.objects.get_or_create(
                name=subcat,
                parent=electronics,
                is_department=False
            )

        self.stdout.write(self.style.SUCCESS('Successfully set up Electronics department')) 