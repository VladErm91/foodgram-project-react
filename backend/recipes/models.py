from django.conf import settings
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator,)
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)
from colorfield.fields import ColorField
from users.models import User


class Ingredient(Model):
    """ Ингридиенты """
    name = CharField(
        max_length=settings.LENGTH_RECIPES_NAME,
        verbose_name='Название ингридиента',
        db_index=True
    )
    measurement_unit = CharField(
        max_length=settings.LENGTH_MEASURE,
        verbose_name='Еденица измерения'
    )

    class Meta():
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingridient'
            )
        ]

    def __str__(self):
        return self.name


class Tag(Model):
    """ Теги"""
    name = CharField(
        verbose_name='Название тега',
        max_length=settings.LENGTH_RECIPES,
        db_index=True,
        unique=True
    )
    color = ColorField(
        verbose_name='HEX-код',
        format='hex',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Проверьте вводимый формат',
            )
        ],
    )
    slug = SlugField(
        max_length=settings.LENGTH_RECIPES,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(Model):
    """ Рецепт """
    author = ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=CASCADE,
        related_name='recipes'
    )
    name = CharField(
        verbose_name='Название рецепта',
        max_length=settings.LENGTH_RECIPES,
    )
    image = ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение'
    )
    text = TextField(verbose_name='Описание')
    ingredients = ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientRecipe'
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[MinValueValidator(
            1, message='Время приготовления не менее 1 минуты!'
        ), MaxValueValidator(
            settings.MAX_COOKING_TIME,
            message='Время приготовления не более 24 часов!'
        )]
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class FavoritesShopCart(Model):
    """Вспогательная модель для избранного и списка покупок"""

    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE
    )

    class Meta:
        abstract = True


class Favorite(FavoritesShopCart):
    """Избранные рецепты"""

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class ShoppingCart(FavoritesShopCart):
    """Список покупок"""

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке у {self.user}'


class IngredientRecipe(Model):
    """ Ингридиенты в рецепте """
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='ingredientforrecipe'
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество ингридиента',
        validators=[MinValueValidator(
            1, message='Колличество ингридиента не может быть менее 1'
        ), MaxValueValidator(
            settings.MAX_INGREDIENT_AMOUNT,
            message='Колличество игридиента не может быть более 32000'
        )]
    )

    class Meta:
        ordering = ('ingredient__name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты рецепта'
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingridient_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )
