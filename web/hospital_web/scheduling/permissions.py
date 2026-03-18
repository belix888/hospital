from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsStaffOrDoctor(BasePermission):
    """
    Basic role model:
    - staff/superuser: full access
    - authenticated doctor user (has user.doctor_profile): limited to own appointments (enforced in viewsets)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return hasattr(request.user, "doctor_profile")

