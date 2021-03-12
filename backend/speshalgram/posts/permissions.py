from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError
from rest_framework.permissions import BasePermission

from speshalgram.accounts.permissions import User, can_view_profile
from speshalgram.posts.models import Post


class IsAbleToViewPostObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return can_view_profile(
            who=request.user,
            whom=obj.owner
        )


class IsAbleToViewPostsList(BasePermission):
    def has_permission(self, request, view):
        try:
            username = view.request.query_params['username']
        except KeyError:
            raise ParseError("you must provide 'username' parameter")
        
        owner = get_object_or_404(User, username=username)

        return can_view_profile(
            who=request.user,
            whom=owner
        )


class IsAbleToViewPostContent(BasePermission):
    def has_permission(self, request, view):
        try:
            post_id = int(view.request.query_params["post_id"])
        except KeyError:
            raise ParseError("you must provide 'post_id' parameter")
        except ValueError:
            raise ParseError("'post_id' must be an integer")

        post = get_object_or_404(
            Post.objects.select_related('owner'), 
            id=post_id
        )

        return can_view_profile(
            who=request.user,
            whom=post.owner
        )


class IsAbleToViewPostComments(IsAbleToViewPostContent):
    pass


class IsAbleToViewPostLikes(IsAbleToViewPostContent):
    pass


class IsAbleToAlterPostContent(IsAbleToViewPostContent):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            super().has_permission(request, view)
        )


class IsAbleToAlterPostComments(IsAbleToAlterPostContent):
    pass


class IsAbleToAlterPostLikes(IsAbleToAlterPostContent):
    pass


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            obj.owner_id == request.user.id
        )


class IsPostOwner(IsOwner):
    pass


class IsCommentOwner(IsOwner):
    pass
