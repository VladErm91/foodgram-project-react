from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorPermission(BasePermission):
    """Делаем так, чтобы изменять и добавлять объекты
       мог только их автор"""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
                
class IsCurrentUserOrAdminOrReadOnly(BasePermission):
    """
    Неавторизованным пользователям разрешён только просмотр.
    Если пользователь является администратором
    или пользователем, то возможны остальные методы.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (obj.id == request.user
                or request.user.is_superuser)
