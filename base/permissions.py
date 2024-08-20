from rest_framework.permissions import BasePermission

class IsAdminOrAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.userprofile.role == 'admin':
            return True
        return obj.author == request.user
