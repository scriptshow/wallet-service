from rest_framework.permissions import BasePermission


class IsCompany(BasePermission):

    """
    Allows access only to company users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_company)
