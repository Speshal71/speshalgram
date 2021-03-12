from django import forms
from django.contrib import admin
from django.contrib.auth import models
from django.forms import widgets

from speshalgram.posts.models import Comment, Like, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'description': forms.Textarea()
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        widgets = {
            'text': forms.Textarea()
        }


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    search_fields = ('owner__username',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
    search_fields = ('^owner__username', '=post__id')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


class LikeAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
