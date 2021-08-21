from rest_framework import request as rq
from rest_framework.permissions import BasePermission, SAFE_METHODS


class CheckIfAdminMixin:
    @staticmethod
    def check_if_admin(request: rq):
        return False if request.user.is_anonymous else request.user.is_admin


class CheckIfModeratorMixin:
    @staticmethod
    def check_if_moderator(request: rq):
        return False if request.user.is_anonymous else request.user.is_moderator


class IsAdmin(BasePermission, CheckIfAdminMixin):
    def has_permission(self, request: rq, view):
        return self.check_if_admin(request)

    def has_object_permission(self, request: rq, view, obj):
        return self.check_if_admin(request)


class IsAuthor(BasePermission):
    def has_object_permission(self, request: rq, view, obj):
        return request.user == obj.author


class IsModerator(BasePermission, CheckIfModeratorMixin):
    def has_permission(self, request, view):
        return self.check_if_moderator(request)

    def has_object_permission(self, request, view, obj):
        return self.check_if_moderator(request)


class IsAdminElseReadOnly(BasePermission, CheckIfAdminMixin):
    def has_permission(self, request: rq, view):
        if request.method in SAFE_METHODS:
            return True
        return self.check_if_admin(request)

    def has_object_permission(self, request: rq, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return self.check_if_admin(request)


class IsAdminOrModeratorOrAuthorElseReadOnly(IsAdminElseReadOnly):
    def has_permission(self, request: rq, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request: rq, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user.is_admin or user.is_moderator or request.user == obj.author
