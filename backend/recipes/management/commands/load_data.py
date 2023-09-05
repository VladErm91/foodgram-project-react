import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ' Загрузить данные в модель ингредиентов '

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Старт команды'))
        with open(settings.INGREDIENTS_PATH, encoding='utf-8',
                  ) as data_file_ingredients:
            ingredient_data = json.loads(data_file_ingredients.read())
            Ingredient.objects.bulk_create(
                  Ingredient(**ingredients)
                  for ingredients in ingredient_data
                  )

        with open(settings.TAGS_PATH, encoding='utf-8',
                  ) as data_file_tags:
            tags_data = json.loads(data_file_tags.read())
            for tags in tags_data:
                Tag.objects.get_or_create(**tags)

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
