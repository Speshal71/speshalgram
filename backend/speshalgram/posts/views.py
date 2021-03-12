from django.conf import settings
from django.db.models import Count, F, OuterRef, Prefetch, Window
from django.db.models.expressions import Exists
from django.db.models.functions import RowNumber
from django_cte import With
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from speshalgram.accounts.models import Subscription, User
from speshalgram.accounts.serializers import ShortUserSerializer
from speshalgram.posts.models import Comment, Like, Post
from speshalgram.posts.permissions import (
    IsAbleToAlterPostComments,
    IsAbleToAlterPostLikes,
    IsAbleToViewPostComments,
    IsAbleToViewPostLikes,
    IsAbleToViewPostObject,
    IsAbleToViewPostsList,
    IsCommentOwner,
    IsPostOwner,
)
from speshalgram.posts.serializers import CommentSerializer, PostSerializer
from speshalgram.utils import PermissionsByActionsMixin


class PostCursorPagination(CursorPagination):
    page_size = settings.POSTS_PER_PAGE
    ordering = ('-date_created', '-id')


class PostViewSet(PermissionsByActionsMixin, ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    pagination_class = PostCursorPagination

    permission_classes_by_actions = {
        'create': [IsAuthenticated],
        'partial_update': [IsPostOwner],
        'destroy': [IsPostOwner],
        'list': [IsAbleToViewPostsList],
        'retrieve': [IsAbleToViewPostObject],
    }
    
    PARTIAL_UPDATE_FIELDS = {'description'}
    
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == 'retrieve':
            context['hide_comments'] = True
        
        return context
    
    def extend_queryset(self, queryset, preview_comments=False):
        """
        adds post owner
        annotates number of likes and if post is liked by the user
        prefetches first N comments if required
        """
        queryset = (
            queryset
            .select_related('owner')
            .annotate(
                nlikes=Count('likes'),
                is_liked_by_me=Exists(
                    Like.objects.filter(
                        post_id=OuterRef('id'),
                        owner_id=self.request.user.id,
                    )
                )
            )
        )

        if preview_comments:
            enumerated_comments_cte = With(
                Comment.objects.annotate(
                    row_number=Window(
                        expression=RowNumber(),
                        partition_by=[F('post_id')],
                        order_by=[F('date_created').desc(), F('id').desc()]
                    )
                )
            )

            queryset = queryset.prefetch_related(
                Prefetch(
                    'comments',
                    queryset=(
                        enumerated_comments_cte.queryset()
                        .with_cte(enumerated_comments_cte)
                        .select_related('owner')
                        .filter(
                            row_number__lte=settings.NUM_OF_PREVIEW_COMMENTS
                        )
                        .order_by('date_created', 'id')
                    ),
                    to_attr='preview_comments'
                )
            )
        
        return queryset

    
    def get_queryset(self):
        orig_queryset = super().get_queryset()

        if self.action == 'retrieve':
            return self.extend_queryset(orig_queryset)
        
        elif self.action == 'list':
            return (
                self.extend_queryset(
                    orig_queryset, 
                    preview_comments=True
                )
                .filter(
                    owner__username=self.request.query_params['username']
                )
                .order_by('-date_created', '-id')
            )

        elif self.action == 'feed':
            return (
                self.extend_queryset(
                    orig_queryset, 
                    preview_comments=True
                )
                .filter(
                    owner__sub_followers__follower=self.request.user,
                    owner__sub_followers__status=Subscription.ACCEPTED,
                )
                .order_by('-date_created', '-id')
            )
        
        return orig_queryset
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        serializer.instance.nlikes = 0
        serializer.instance.preview_comments = []
    
    def update(self, request, *args, **kwargs):
        if self.action == 'update':
            raise MethodNotAllowed(request.method)

        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        if not (set(request.data.keys()) <= self.PARTIAL_UPDATE_FIELDS):
            raise ParseError(
                f'only {self.PARTIAL_UPDATE_FIELDS} fields are allowed!'
            )

        return super().partial_update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def feed(self, request, *args, **kwargs):
        # reuse list pagination functionality
        return self.list(request, *args, **kwargs)


class CommentCursorPagination(CursorPagination):
    page_size = settings.COMMENTS_PER_PAGE
    ordering = ('-date_created', '-id')


class CommentViewSet(PermissionsByActionsMixin, ModelViewSet):
    queryset = Comment.objects.select_related('owner')
    serializer_class = CommentSerializer

    pagination_class = CommentCursorPagination
    
    permission_classes = [IsCommentOwner]
    permission_classes_by_actions = {
        'list': [IsAbleToViewPostComments],
        'create': [IsAbleToAlterPostComments]
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == 'list':
            queryset = (
                queryset
                .filter(post_id=self.request.query_params['post_id'])
                .order_by('-date_created', '-id')
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
       raise MethodNotAllowed(request.method)
    
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            post_id=self.request.query_params['post_id']
        )


class LikeCursorPagination(CursorPagination):
    page_size = settings.LIKES_PER_PAGE
    ordering = 'id'


class LikeAPIView(GenericAPIView):
    pagination_class = LikeCursorPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAbleToViewPostLikes()]
        elif self.request.method in {'PUT', 'DELETE'}:
            return [IsAbleToAlterPostLikes()]

        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        post_id = request.query_params['post_id']
        queryset = User.objects.filter(likes__post_id=post_id).order_by('id')
        page = self.paginate_queryset(queryset)
        serializer = ShortUserSerializer(
            page, 
            many=True, 
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    def put(self, request, *args, **kwargs):
        post_id = request.query_params['post_id']
        Like.objects.get_or_create(owner=request.user, post_id=post_id)
        nlikes = Like.objects.filter(post_id=post_id).count()

        return Response(
            data={'nlikes': nlikes},
            status=HTTP_200_OK
        )
    
    def delete(self, request, *args, **kwargs):
        post_id = request.query_params['post_id']
        Like.objects.filter(owner=request.user, post_id=post_id).delete()
        nlikes = Like.objects.filter(post_id=post_id).count()

        return Response(
            data={'nlikes': nlikes},
            status=HTTP_200_OK
        )
