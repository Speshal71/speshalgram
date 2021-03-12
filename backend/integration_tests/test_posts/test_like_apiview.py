import pytest
from django.urls import reverse
from rest_framework import status

from speshalgram.posts.models import Like


# TODO add query count
@pytest.mark.likes
@pytest.mark.django_db
class TestLikeAPIView:

    LIKE_FIELDS = {
        'username',
        'first_name',
        'last_name',
        'avatar',
    }

    @pytest.mark.parametrize(
        ('user',),
        (
            (None,),
            ('user2',),
        )
    )
    def test_get_likes_for_open_post(
        self,
        user,
        client,
        user2,
        user2_posts
    ):
        post = user2_posts[0]['post']
        likes_usernames = [
            like.owner.username
            for like in sorted(user2_posts[0]['likes'], key=lambda l: l.owner_id)
        ]

        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()['results']
        assert response_json[0].keys() == self.LIKE_FIELDS
        assert (
            [like['username'] for like in response_json] == 
            likes_usernames
        )

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', status.HTTP_403_FORBIDDEN),
            ('u2_accepted_follower', status.HTTP_200_OK),
            ('user2_closed', status.HTTP_200_OK),
        )
    )
    def test_get_likes_for_closed_post(
        self,
        user,
        expected_status,
        client,
        user1,
        user2_closed,
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts
    ):
        post = user2_posts[0]['post']
        likes_usernames = [
            like.owner.username
            for like in sorted(user2_posts[0]['likes'], key=lambda l: l.owner_id)
        ]
        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        response = client.get(url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            response_json = response.json()['results']
            assert response_json[0].keys() == self.LIKE_FIELDS
            assert (
                [like['username'] for like in response_json] == 
                likes_usernames
            )
    
    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_200_OK),
        )
    )
    def test_like_open_post(
        self,
        user,
        expected_status,
        client,
        user1,
        user2,
        user2_posts,
    ):
        post = user2_posts[0]['post']
        nlikes = len(user2_posts[0]['likes'])

        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        if expected_status == status.HTTP_200_OK:
            for i in range(2):
                response = client.put(url)      
                assert response.status_code == expected_status
                assert Like.objects.filter(post=post).count() == nlikes + 1
        else:
            response = client.put(url)      
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes
    
    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', status.HTTP_403_FORBIDDEN),
            ('u2_accepted_follower', status.HTTP_200_OK),
            ('user2_closed', status.HTTP_200_OK),
        )
    )
    def test_like_closed_post(
        self,
        user,
        expected_status,
        client,
        user1,
        user2_closed,
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts,
    ):
        post = user2_posts[0]['post']
        nlikes = len(user2_posts[0]['likes'])

        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        if expected_status == status.HTTP_200_OK:
            for i in range(2):
                response = client.put(url)      
                assert response.status_code == expected_status
                assert Like.objects.filter(post=post).count() == nlikes + 1
        else:
            response = client.put(url)      
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes
            
    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_200_OK),
        )
    )
    def test_delete_like_for_open_post(
        self,
        user,
        expected_status,
        client,
        user1,
        user2,
        user2_posts,
    ):
        post = user2_posts[0]['post']
        nlikes = len(user2_posts[0]['likes'])

        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        if expected_status == status.HTTP_200_OK:
            # make like first
            response = client.put(url)
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes + 1     

            for i in range(2):
                response = client.delete(url)      
                assert response.status_code == expected_status
                assert Like.objects.filter(post=post).count() == nlikes
        else:
            response = client.delete(url)      
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', status.HTTP_403_FORBIDDEN),
            ('u2_accepted_follower', status.HTTP_200_OK),
            ('user2_closed', status.HTTP_200_OK),
        )
    )
    def test_delete_like_for_closed_post(
        self,
        user,
        expected_status,
        client,
        user1,
        user2_closed,
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts,
    ):
        post = user2_posts[0]['post']
        nlikes = len(user2_posts[0]['likes'])

        user = vars().get(user)
        url = reverse('likes') + f'?post_id={post.id}'

        client.force_authenticate(user)

        if expected_status == status.HTTP_200_OK:
            # make like first
            response = client.put(url)
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes + 1     

            for i in range(2):
                response = client.delete(url)      
                assert response.status_code == expected_status
                assert Like.objects.filter(post=post).count() == nlikes
        else:
            response = client.delete(url)      
            assert response.status_code == expected_status
            assert Like.objects.filter(post=post).count() == nlikes
