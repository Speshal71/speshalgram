from pathlib import Path
from uuid import uuid4

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class Subscription(models.Model):
    ACCEPTED = 'a'
    PENDING = 'p'
    REJECTED = 'r'
    STATUSES = (
        (ACCEPTED, 'Accepted'),
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
    )

    status = models.CharField(choices=STATUSES, max_length=1)
    follower = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE,
        related_name='sub_follows_to'
    )
    follows_to = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE,
        related_name='sub_followers'
    )
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'follows_to'],
                name='unique_subscription'
            ),
        ]

    def __str__(self) -> str:
        follower = self.follower.username
        follows_to = self.follows_to.username
        status = dict(self.STATUSES)[self.status]
        return f'{follower} follows {follows_to} ({status})'


class CustomUserQuerySet(models.QuerySet):
    def filter_followers_of(self, user, status=Subscription.ACCEPTED):
        filters = {}
        if isinstance(user, str):
            filters['sub_follows_to__follows_to__username'] = user
        else:
            filters['sub_follows_to__follows_to'] = user
        
        if status:
            filters['sub_follows_to__status'] = status
        
        return self.filter(**filters)

    def filter_follows_of(self, user, status=Subscription.ACCEPTED):
        filters = {}
        if isinstance(user, str):
            filters['sub_followers__follower__username'] = user
        else:
            filters['sub_followers__follower'] = user
        
        if status:
            filters['sub_followers__status'] = status
        
        return self.filter(**filters)


class CustomUserManager(UserManager.from_queryset(CustomUserQuerySet)):
    use_in_migrations = True


def avatar_path(user, filename):
    extension = filename.split('.')[-1]
    return str(Path(str(user.id), f'{uuid4()}.{extension}'))


class User(AbstractUser):
    description = models.CharField(
        max_length=200, 
        null=True, 
        blank=True
    )
    avatar = models.ImageField(
        upload_to=avatar_path, 
        default='default_avatar.png'
    )
    is_opened = models.BooleanField(default=True)

    objects = CustomUserManager()
