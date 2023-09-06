from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag)
from users.models import User


class CustomUserSerializer(UserSerializer):
    """ Сериализатор пользователя """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not self.context.get('request').user.is_anonymous:
            return obj.following.filter(user=request.user).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class SubscribeListSerializer(UserSerializer):
    """ Сериализатор подписок """
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        limit_numb = int(limit)
        if limit_numb:
            recipes = recipes[: limit_numb]
        else:
            raise ValidationError(
                'Не возможно преобразовать строку в число'
            )
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
    return serializer.data


class TagSerializer(ModelSerializer):
    """ Сериализатор просмотра тегов """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """ Сериализатор просмотра ингридиентов """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientRecipeSerializer(ModelSerializer):
    """ Сериализатор связи ингридиентов и рецепта """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ReadIngredientRecipeSerializer(ModelSerializer):
    """Сериализатор для прочтения ингредиентов в рецепте"""

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('amount',)


class ReadRecipeSerializer(ModelSerializer):
    """Сериализатор для прочтения рецепта"""

    author = UserSerializer(read_only=True)
    ingredients = ReadIngredientRecipeSerializer(
        many=True, read_only=True, source='ingredientforrecipe'
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class IngredientRecipeCreateSerializer(ModelSerializer):
    """Сериализатор создания ингредиентов для рецепта"""

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(
        write_only=True,
        min_value=1,
        max_value=settings.MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(ModelSerializer):
    """Сериализатор создания и изменения рецепта """

    ingredients = IngredientRecipeCreateSerializer(
        many=True, source='ingredient'
    )
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    cooking_time = IntegerField(
        write_only=True,
        min_value=1,
        max_value=settings.MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'cooking_time', 'text'
        )
        read_only_fields = ('author',)

    def validate_tags(self, data):
        """Валидация тегов."""
        tags = data
        tags_list = []
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise ValidationError(
                    'Количество тегов не может быть менее 1!'
                )
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальны'}
                )
        tags_list.append(tag)
        return data

    def validate_ingredients(self, ingredients):
        """Валидация ингридиентов."""

        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствуют ингридиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента больше 0')
            return ingredients

    def ingredient_recipe_bulk_create(self, ingredients, recipe):
        """Создание ингредиентов рецепта."""

        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создание рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.save()
        self.ingredient_recipe_bulk_create(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.save()
        self.ingredient_recipe_bulk_create(ingredients, instance)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(ModelSerializer):
    """ Сериализатор полей краткого отображения рецептов
    для избранного и листа покупок """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
