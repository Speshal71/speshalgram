from unittest import mock
from uuid import uuid4

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from speshalgram.accounts.models import Subscription, User
from speshalgram.posts.models import Comment, Like, Post


@pytest.fixture(autouse=True)
def mock_filestorage():
    with mock.patch(
        'django.core.files.storage.FileSystemStorage.save',
        new=lambda *args, **kwargs: 'test.gif'
    ):
        yield


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        kwargs['username'] = kwargs.get('username', str(uuid4()))
        return User.objects.create(**kwargs)
    return _create_user


@pytest.fixture
def user1(create_user):
    return create_user()


@pytest.fixture()
def user2(create_user):
    return create_user()


@pytest.fixture
def user2_closed(user2):
    user2.is_opened=False
    user2.save()
    return user2


user3 = user1
user4 = user1
user5 = user1


@pytest.fixture
def u1_accepted_follower(create_user, user1):
    follower = create_user()
    Subscription.objects.create(
        follower=follower,
        follows_to=user1,
        status=Subscription.ACCEPTED
    )
    return follower


u1_accepted_follower_2 = u1_accepted_follower


@pytest.fixture
def u2_accepted_follower(create_user, user2):
    follower = create_user()
    Subscription.objects.create(
        follower=follower,
        follows_to=user2,
        status=Subscription.ACCEPTED
    )
    return follower


@pytest.fixture
def u1_pending_follower(create_user, user1):
    follower = create_user()
    Subscription.objects.create(
        follower=follower,
        follows_to=user1,
        status=Subscription.PENDING
    )
    return follower


@pytest.fixture
def u2_pending_follower(create_user, user2):
    follower = create_user()
    Subscription.objects.create(
        follower=follower,
        follows_to=user2,
        status=Subscription.PENDING
    )
    return follower


u2_pending_follower_2 = u2_pending_follower


@pytest.fixture
def u2_accepted_following(create_user, user2):
    follows_to = create_user()
    Subscription.objects.create(
        follower=user2,
        follows_to=follows_to,
        status=Subscription.ACCEPTED
    )
    return follows_to


@pytest.fixture
def u2_pending_following(create_user, user2):
    follows_to = create_user()
    Subscription.objects.create(
        follower=user2,
        follows_to=follows_to,
        status=Subscription.PENDING
    )
    return follows_to


@pytest.fixture
def u2_accepted_follower_who_liked_his_posts(create_user, user2):
    follower = create_user()
    Subscription.objects.create(
        follower=follower,
        follows_to=user2,
        status=Subscription.ACCEPTED
    )
    return follower


@pytest.fixture
def test_gif():
    return (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )


@pytest.fixture
def user2_posts(
    test_gif, 
    user2, 
    user3, 
    user4, 
    u2_accepted_follower_who_liked_his_posts
):
    posts_spec = [
        (
            ['comment'] * (settings.NUM_OF_PREVIEW_COMMENTS + 2),
            [user3, user4, u2_accepted_follower_who_liked_his_posts]
        ),
        (
            ['c1', 'c2'],
            [user4, u2_accepted_follower_who_liked_his_posts]
        )
    ]
    posts = []
    for comments, likes in posts_spec:
        post = Post.objects.create(
            owner=user2,
            picture=SimpleUploadedFile(
                'test.gif', 
                test_gif, 
                content_type='image/gif'
            ),
            description='text'
        )
        comments = [
            Comment.objects.create(owner=user3, post=post, text=comment_text)
            for comment_text in comments
        ]
        likes = [
            Like.objects.create(owner=owner, post=post)
            for owner in likes
        ]
        posts.append({
            'post': post,
            'comments': comments,
            'likes': likes,
        })
    
    return posts


@pytest.fixture
def user2_closed_posts(user2_closed, user2_posts):
    return user2_posts
