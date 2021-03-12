from django.conf import settings
from django.db.models import OuterRef, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from speshalgram.accounts.models import Subscription, User
from speshalgram.accounts.permissions import (
    IsOpenOrSubcribedByMe,
    ObjectIsNotMe,
)
from speshalgram.accounts.serializers import (
    CreateUserSerializer,
    ShortUserSerializer,
    UserSerializer,
)
from speshalgram.utils import SubqueryCount


class UserCursorPagination(CursorPagination):
    page_size = settings.USERS_PER_PAGE
    ordering = 'id'


class UserViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in {
            'retrieve', 'subscribe', 'cancel_subscribtion', 'accept', 'reject'
        }:
            queryset = queryset.annotate(
                nfollowers=SubqueryCount(
                    User.objects.filter_followers_of(OuterRef('id'))
                ),
                nfollows=SubqueryCount(
                    User.objects.filter_follows_of(OuterRef('id'))
                ),
                followed_by_me_status=(
                    Subscription.objects.filter(
                        follower_id=self.request.user.id,
                        follows_to_id=OuterRef('id')
                    ).values('status')
                ),
            )
        
        elif self.action == 'list':
            queryset = (
                queryset.filter(
                    username__startswith=self.request.query_params['search']
                )
                .all()[:settings.SEARCH_NUM_OF_SUGGESTED_USERS]
            )
        
        elif self.action == 'followers':
            queryset = (
                queryset
                .filter_followers_of(self.kwargs['username'])
                .order_by('id')
            )
        
        elif self.action == 'follows':
            queryset = (
                queryset
                .filter_follows_of(self.kwargs['username'])
                .order_by('id')
            )
        
        elif self.action == 'pending_followers':
            queryset = (
                queryset
                .filter_followers_of(
                    self.request.user,
                    Subscription.PENDING
                )
                .order_by('id')
            )

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer

        elif self.action in {
            'list', 'followers', 'follows', 'pending_followers'    
        }:
            return ShortUserSerializer
        
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        if self.action == 'list' and 'search' not in request.query_params:
            raise ParseError('you must provide "search" parameter')
        
        return super().list(request, *args, **kwargs)
    
    @action(
        detail=True, 
        methods=['GET'],
        permission_classes=[IsOpenOrSubcribedByMe],
        pagination_class = UserCursorPagination, 
    )
    def followers(self, request, **kwargs):
        # reuse paginaton functionality provided by list()
        return self.list(request, **kwargs)
    
    @action(
        detail=True, 
        methods=['GET'],
        permission_classes=[IsOpenOrSubcribedByMe],
        pagination_class = UserCursorPagination
    )
    def follows(self, request, **kwargs):
        # reuse paginaton functionality provided by list()
        return self.list(request, **kwargs)
    
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def pending_followers(self, request, **kwargs):
        return self.list(request, **kwargs)

    @action(
        detail=False, 
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, **kwargs):
        return Response(
            data={'username': request.user.username},
            status=status.HTTP_200_OK
        )
    
    @me.mapping.patch
    def patch_me(self, request, **kwargs):
        user_was_opened = request.user.is_opened

        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if user_was_opened and not request.user.is_opened:
            Subscription.objects.filter(
                follows_to=request.user, 
                status=Subscription.PENDING
            ).delete()

        return Response(serializer.data)
    
    @action(
        detail=True,
        methods=['PUT'],
        permission_classes=[ObjectIsNotMe]
    )
    def subscribe(self, request, **kwargs):
        whom = get_object_or_404(User, username=self.kwargs['username'])
        
        new_subscription_status = (
            Subscription.ACCEPTED 
            if whom.is_opened 
            else Subscription.PENDING
        )

        subscription, created = (
            Subscription.objects.get_or_create(
                follower=request.user,
                follows_to=whom,
                defaults={'status': new_subscription_status}
            )
        )

        if not created and subscription.status == Subscription.REJECTED:
            subscription.status = new_subscription_status
            subscription.save(update_fields=['status'])
        
        updated_whom = self.get_object()
        serializer = self.get_serializer(updated_whom)

        return Response(serializer.data)

    @subscribe.mapping.delete
    def cancel_subscribtion(self, request, **kwargs):
        whom = get_object_or_404(User, username=self.kwargs['username'])

        Subscription.objects.filter(
            follower=request.user, 
            follows_to=whom
        ).delete()

        updated_whom = self.get_object()
        serializer = self.get_serializer(updated_whom)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['PUT'],
        permission_classes=[ObjectIsNotMe]
    )
    def accept(self, request, **kwargs):
        whom = get_object_or_404(User, username=self.kwargs['username'])

        accepted = (
            Subscription.objects
            .filter(
                (
                    Q(status=Subscription.ACCEPTED) | 
                    Q(status=Subscription.PENDING)
                ),
                follower=whom, 
                follows_to=request.user,
            )
            .update(status=Subscription.ACCEPTED)
        )

        if not accepted:
            raise NotFound({
                'detail': 'This user didn\'t send you subscription request'
            })

        return Response(status=status.HTTP_200_OK)

    @accept.mapping.delete
    def reject(self, request, **kwargs):
        whom = get_object_or_404(User, username=self.kwargs['username'])

        Subscription.objects.filter(
            follower=whom, 
            follows_to=request.user
        ).delete()

        return Response(status=status.HTTP_200_OK)
