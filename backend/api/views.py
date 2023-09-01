from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)

from .filters import (RecipeFilter)
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (CreateRecipeSerializer, RecipeShortSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          TagSerializer)


class TagViewSet(ModelViewSet):
    """ Вьюсет тегов """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientsViewSet(ModelViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    def get_queryset(self):

        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__istartswith=name.lower())
        return queryset


class RecipeViewSet(ModelViewSet):
    """ Вьюсет рецептов """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorPermission)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend, )

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от
        того выводится рецепт или создается"""

        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_to_base(self, request, model, pk):
        """ Функция добавления рецепта """

        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(
            recipe=recipe, user=request.user
        )
        if created:
            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete_from_base(self, user, model, pk):
        """ Функция удаления рецепта """

        recipe = get_object_or_404(Recipe, pk=pk)
        databse_obj = model.objects.filter(
            user=user, recipe=recipe
        )
        if not databse_obj.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        databse_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        url_path='favorite',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Функция добавления и удаления рецепта из избранного."""

        if request.method == 'POST':
            return self.add_to_base(request, Favorite, pk)
        return self.delete_from_base(request.user, Favorite, pk)

    @action(
        methods=('post', 'delete'),
        url_path='shopping_cart',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """ Функция добавления и удаления рецепта из списка покупок."""

        if request.method == 'POST':
            return self.add_to_base(request, ShoppingCart, pk)
        return self.delete_from_base(request.user, ShoppingCart, pk)

    @action(
        methods=('get',),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shopping_cart__user=request.user)
        shopping_cart = IngredientRecipe.objects.filter(
            recipe__in=recipes).values(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit')).order_by(
            'ingredient__name').annotate(total=Sum('amount'))
        ingr_list = []
        for recipe in shopping_cart:
            ingr_list.append(recipe)
        shopping_list = 'Купить в магазине:'
        for ingredient in shopping_cart:
            shopping_list += (f'{ingredient["name"]}: '
                              f'{ingredient["total"]}'
                              f'{ingredient["units"]}.\n')
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response
