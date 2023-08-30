from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User

from .filters import (RecipeFilter, IngredientFilter)
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (CreateRecipeSerializer, RecipeShortSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          SubscribeListSerializer, TagSerializer,
                          UserSerializer)


class TagViewSet(ModelViewSet):
    """ Вьюсет тегов """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class UserViewSet(UserViewSet):
    """ Вьюсет пользователя """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorPermission)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """ Функция добавления подписки """

        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
	return None
	
    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """ Функция вывода листа подписок """

        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


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
        """ Функция для загрузки списка покупок в формате .txt"""

        ingredients = IngredientRecipe.objects.filter(
            recipe__shop_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))
        wishlist = ''
        for ingredient in ingredients:
            wishlist += (f'{ingredient["ingredient__name"]}: '
                         f'{ingredient["total_sum"]}')
            wishlist += f'{ingredient["ingredient__measurement_unit"]}.\n'
        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=wishlist.txt'
        return response


class IngredientsViewSet(ModelViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientFilter, )

    def get_queryset(self):

        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__istartswith=name.lower())
        return queryset
