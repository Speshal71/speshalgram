from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from speshalgram.accounts.models import Subscription, User


def can_view_profile(who, whom):
    if not who.is_authenticated:
        return whom.is_opened
    
    return (
        whom.is_opened or 
        who.id == whom.id or
        Subscription.objects.filter(
            follower=who,
            follows_to=whom,
            status=Subscription.ACCEPTED
        ).exists()
    )


class IsOpenOrSubcribedByMe(BasePermission):
    def has_permission(self, request, view):
        requested_user = get_object_or_404(
            User, 
            username=view.kwargs['username']
        )
        return can_view_profile(
            who=request.user,
            whom=requested_user
        )


class ObjectIsNotMe(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.username == view.kwargs['username']:
            raise ValidationError({
                'detail': 'you can\'t make request over yourself'
            })
        
        return True
