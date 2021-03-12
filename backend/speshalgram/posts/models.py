from pathlib import Path
from uuid import uuid4

from django.db import models
from django_cte import CTEManager

from speshalgram.accounts.models import User


def picture_path(post, filename):
    extension = filename.split('.')[-1]
    return str(Path(str(post.owner.id), f'{uuid4()}.{extension}'))


class DateTimeMixin(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# TODO date_created db_index?
class Post(DateTimeMixin, models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    picture = models.ImageField(upload_to=picture_path)
    description = models.CharField(
        max_length=500, 
        null=True, 
        blank=True
    )

    def __str__(self) -> str:
        return f'post {self.id} of {self.owner.username}'

# TODO date_created db_inex?
class Comment(DateTimeMixin, models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.CharField(max_length=200)

    objects = CTEManager()

    def __str__(self) -> str:
        return f'comment of {self.owner.username} to post {self.post_id}'


class Like(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'post'],
                name='only_like_constraint'
            ),
        ]
    
    def __str__(self) -> str:
        return f'like of {self.owner.username} to {self.post_id}'
