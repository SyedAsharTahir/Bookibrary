from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Clear all data from the database'

    def handle(self, *args, **options):
        # Get all models except migrations
        models = []
        for model in apps.get_app_config('library').get_models():
            if not model._meta.db_table.startswith('django_'):
                models.append(model)
        
        # Delete all instances
        for model in models:
            model.objects.all().delete()
            self.stdout.write(f'Cleared {model._meta.model_name}')
        
        self.stdout.write(self.style.SUCCESS('All data cleared from database'))
