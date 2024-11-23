from django.core.management.base import BaseCommand
from store.models import Category

class Command(BaseCommand):
    help = 'Sets up initial data for the store'

    def handle(self, *args, **kwargs):
        # Create default category
        default_category, created = Category.objects.get_or_create(
            name='Uncategorized',
            slug='uncategorized'
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created default category')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Default category already exists')
            ) 