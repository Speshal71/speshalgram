from django.conf import settings
from rest_framework import serializers

from speshalgram.accounts.serializers import ShortUserSerializer
from speshalgram.posts.models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    owner = ShortUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'owner', 'text')


class PostSerializer(serializers.ModelSerializer):
    owner = ShortUserSerializer(read_only=True)
    nlikes = serializers.SerializerMethodField()
    preview_comments = serializers.SerializerMethodField()
    is_liked_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 
            'owner', 
            'picture', 
            'description', 
            'nlikes', 
            'preview_comments',
            'is_liked_by_me'
        )
        
    def get_fields(self):
        fields = super().get_fields()

        if self.context.get('hide_comments'):
            fields.pop('preview_comments')
        
        return fields
    
    def get_nlikes(self, obj):
        if hasattr(obj, 'nlikes'):
            nlikes = obj.nlikes
        else:
            nlikes = obj.likes.count()
        
        return nlikes

    def get_preview_comments(self, obj):
        if hasattr(obj, 'preview_comments'):
            comments = obj.preview_comments
        else:
            comments = (
                obj.comments
                .select_related('owner')
                .order_by('date_created')[
                    0:settings.NUM_OF_PREVIEW_COMMENTS
                ]
            )
        
        serializer = CommentSerializer(
            comments, 
            many=True, 
            context=self.context
        )

        return serializer.data
