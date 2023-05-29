from rest_framework.permissions import (
    IsAuthenticated,
    BasePermission,
)
from .models import *


class IsAdminUser_ForAdmin(BasePermission):
    def has_permission(self, request, view):
        # import pdb;pdb.set_trace()
        return bool(
            request.user and request.user.is_staff and request.user.is_superuser
        )


