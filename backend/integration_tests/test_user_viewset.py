from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status

from speshalgram.accounts.models import Subscription, User


class AnyStr(str):
    def __eq__(self, other):
        return isinstance(other, str)


# TODO add query count
@pytest.mark.users
@pytest.mark.django_db
class TestUserViewSet:

    @pytest.mark.parametrize(
        ('who', 'whom', 'nfollowers', 'nfollows', 'followed_by_me_status'),
        (
            (None, 'user1', 2, 0, None),
            ('user3', 'user1', 2, 0, None),
            (None, 'user2_closed', 1, 1, None),
            ('user3', 'user2_closed', 1, 1, None),
            ('u2_accepted_follower', 'user2_closed', 1, 1, 'Accepted'),
            ('u2_pending_follower', 'user2_closed', 1, 1, 'Pending'),
            ('user2_closed', 'user2_closed', 1, 1, 'self'),
        )
    )
    def test_watch_profile(
        self, 
        who,
        whom,
        nfollowers,
        nfollows,
        followed_by_me_status,
        client, 
        user1,
        user2_closed,
        user3,
        u1_accepted_follower,
        u1_accepted_follower_2,
        u1_pending_follower,
        u2_accepted_follower,
        u2_pending_follower,
        u2_accepted_following
    ):
        who = vars().get(who, None)
        whom = vars()[whom]
        
        client.force_authenticate(user=who)
        response = client.get(reverse('user-detail', args=[whom.username]))

        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert response_json == {
            'username': whom.username,
            'first_name': whom.first_name,
            'last_name': whom.last_name,
            'avatar': AnyStr(),
            'description': whom.description,
            'is_opened': whom.is_opened,
            'nfollowers': nfollowers,
            'nfollows': nfollows,
            'followed_by_me_status': followed_by_me_status
        }
    
    @pytest.mark.parametrize(
        ('who', 'whom', 'status'),
        (
            (None, 'user2_closed', status.HTTP_401_UNAUTHORIZED),
            ('user1', 'user2_closed', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', 'user2_closed', status.HTTP_403_FORBIDDEN),
        )
    )
    def test_get_followers_forbidden(
        self, 
        who,
        whom,
        status,
        client,
        user1,
        user2_closed,
        u2_pending_follower
    ):
        who = vars().get(who, None)
        whom = vars()[whom]

        client.force_authenticate(user=who)
        response = client.get(reverse('user-followers', args=[whom.username]))

        assert response.status_code == status

    @pytest.mark.parametrize(
        ('who', 'whom', 'followers'),
        (
            (
                None, 
                'user1', 
                ['u1_accepted_follower', 'u1_accepted_follower_2']
            ),
            (
                'user3', 
                'user1',
                ['u1_accepted_follower', 'u1_accepted_follower_2']
            ),
            (
                'u2_accepted_follower', 
                'user2_closed', 
                ['u2_accepted_follower']
            ),
            (
                'user2_closed', 
                'user2_closed', 
                ['u2_accepted_follower']
            ),
        )
    )
    def test_get_followers(
        self, 
        who,
        whom,
        followers,
        client, 
        user1,
        user2_closed,
        user3,
        u1_accepted_follower,
        u1_accepted_follower_2,
        u1_pending_follower,
        u2_accepted_follower,
        u2_pending_follower
    ):
        who = vars().get(who, None)
        whom = vars()[whom]

        for i in range(len(followers)):
            followers[i] = vars()[followers[i]]

        client.force_authenticate(user=who)

        with mock.patch(
            'speshalgram.accounts.views.UserCursorPagination', 
            None
        ):
            url = reverse('user-followers', args=[whom.username])
            response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        returned_followers = response.json()['results']
        assert len(followers) == len(returned_followers)
        assert returned_followers == [
            {
                'username': f.username,
                'avatar': AnyStr(),
                'first_name': f.first_name,
                'last_name': f.last_name,
            }
            for f in sorted(followers, key=lambda f: f.id)
        ]
    
    @pytest.mark.parametrize(
        ('who', 'whom', 'status'),
        (
            (None, 'user2_closed', status.HTTP_401_UNAUTHORIZED),
            ('user1', 'user2_closed', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', 'user2_closed', status.HTTP_403_FORBIDDEN),
        )
    )
    def test_get_follows_forbidden(
        self, 
        who,
        whom,
        status,
        client,
        user1,
        user2_closed,
        u2_pending_follower
    ):
        who = vars().get(who, None)
        whom = vars()[whom]

        client.force_authenticate(user=who)
        response = client.get(reverse('user-follows', args=[whom.username]))

        assert response.status_code == status
    
    @pytest.mark.parametrize(
        ('who', 'whom', 'follows'),
        (
            (
                None, 
                'u1_accepted_follower', 
                ['user1']
            ),
            (
                'user3', 
                'u1_accepted_follower', 
                ['user1']
            ),
            (
                'u2_accepted_follower',
                'user2_closed',
                ['u2_accepted_following']
            ),
            (
                'user2_closed',
                'user2_closed',
                ['u2_accepted_following']
            ),
        )
    )
    def test_get_follows(
        self, 
        who,
        whom,
        follows,
        client, 
        user1,
        user2_closed,
        user3,
        u1_accepted_follower,
        u2_accepted_follower,
        u2_accepted_following,
        u2_pending_following
    ):
        who = vars().get(who, None)
        whom = vars()[whom]

        for i in range(len(follows)):
            follows[i] = vars()[follows[i]]

        client.force_authenticate(user=who)

        with mock.patch(
            'speshalgram.accounts.views.UserCursorPagination', 
            None
        ):
            url = reverse('user-follows', args=[whom.username])
            response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

        returned_follows = response.json()['results']        
        assert len(follows) == len(returned_follows)
        assert returned_follows == [
            {
                'username': f.username,
                'avatar': AnyStr(),
                'first_name': f.first_name,
                'last_name': f.last_name,
            }
            for f in sorted(follows, key=lambda f: f.id)
        ]

    def test_get_pending_followers(
        self, 
        client, 
        user2_closed,
        u2_accepted_follower,
        u2_pending_follower,
        u2_pending_follower_2
    ):
        client.force_authenticate(user=user2_closed)

        response = client.get(reverse('user-pending-followers'))

        assert response.status_code == status.HTTP_200_OK

        returned_pending_followers = response.json()
        expected_pending_followers = [
            u2_pending_follower, u2_pending_follower_2
        ]

        assert (
            len(returned_pending_followers) == len(expected_pending_followers)
        )
        assert returned_pending_followers == [
            {
                'username': f.username,
                'avatar': AnyStr(),
                'first_name': f.first_name,
                'last_name': f.last_name,
            }
            for f in sorted(expected_pending_followers, key=lambda f: f.id)
        ]

    def test_search_user(self, client, create_user):
        nusers = settings.SEARCH_NUM_OF_SUGGESTED_USERS + 2
        for i in range(nusers):
            create_user(username=('a' * (i + 1)))
        
        response = client.get(reverse('user-list') + '?search=a')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == settings.SEARCH_NUM_OF_SUGGESTED_USERS

        response = client.get(reverse('user-list') + f'?search={"a" * 4}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4
    
    def test_get_me(self, client, user1):
        client.force_authenticate(user1)
        response = client.get(reverse('user-me'))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'username': user1.username}

    def test_patch_me(
        self, 
        client, 
        user2,
        u2_accepted_follower,
        u2_pending_follower, 
        u2_pending_follower_2
    ):
        client.force_authenticate(user2)
        response = client.patch(
            reverse('user-me'), 
            data={
                'first_name': 'George',
                'last_name': 'Washington',
                'is_opened': False,
            }
        )
        assert response.status_code == status.HTTP_200_OK
        user2.refresh_from_db()
        assert user2.first_name == 'George'
        assert user2.last_name == 'Washington'
        assert user2.is_opened == False
        npending = (
            User.objects.filter_followers_of(
                user2, 
                status=Subscription.PENDING
            ).count()
        )
        assert npending == 0

    @pytest.mark.parametrize(
        ('who', 'whom', 'status'),
        (
            (None, 'user1', status.HTTP_401_UNAUTHORIZED),
            ('user1', 'user1', status.HTTP_400_BAD_REQUEST),
        )
    )
    def test_subscribe_forbidden(self, client, who, whom, status, user1):
        who = vars().get(who)
        whom = vars().get(whom)

        client.force_authenticate(who)

        url = reverse('user-subscribe', args=[whom.username])
        response = client.put(url)

        assert response.status_code == status

    @pytest.mark.parametrize(
        ('who', 'whom', 'subscription_status'),
        (
            ('user3', 'user1', Subscription.ACCEPTED),
            ('user3', 'user2_closed', Subscription.PENDING),
        )
    )
    def test_subscribe(
        self,
        client,
        who,
        whom,
        subscription_status,
        user1, 
        user2_closed,
        user3
    ):
        who = vars().get(who)
        whom = vars().get(whom)

        client.force_authenticate(who)

        url = reverse('user-subscribe', args=[whom.username])
        response = client.put(url)

        assert response.status_code == status.HTTP_200_OK
        new_subcription = (
            Subscription.objects.filter(follower=who, follows_to=whom).get()
        )
        assert new_subcription.status == subscription_status

    @pytest.mark.parametrize(
        ('who', 'whom'),
        (
            ('user1', 'user2_closed'),
            ('u2_accepted_follower', 'user2_closed'),
            ('u2_pending_follower', 'user2_closed')
        )
    )
    def test_delete_subscription(
        self,
        client,
        who,
        whom,
        user1,
        user2_closed,
        u2_accepted_follower,
        u2_pending_follower
    ):
        who = vars().get(who)
        whom = vars().get(whom)

        client.force_authenticate(who)

        url = reverse('user-subscribe', args=[whom.username])
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        subscription_exists = (
            Subscription.objects.filter(follower=who, follows_to=whom).exists()
        )
        assert not subscription_exists

    @pytest.mark.parametrize(
        ('who', 'whom', 'status'),
        (
            (None, 'user1', status.HTTP_401_UNAUTHORIZED),
            ('user1', 'user1', status.HTTP_400_BAD_REQUEST),
            ('user1', 'user2', status.HTTP_404_NOT_FOUND)
        )
    )
    def test_accept_subscription_forbidden(
        self, 
        client,
        who,
        whom,
        status,
        user1,
        user2
    ):
        who = vars().get(who)
        whom = vars().get(whom)

        client.force_authenticate(who)

        url = reverse('user-accept', args=[whom.username])
        response = client.put(url)

        assert response.status_code == status

    def test_accept_subscription(
        self, 
        client, 
        user2_closed, 
        u2_pending_follower
    ): 
        client.force_authenticate(user2_closed)
        
        url = reverse('user-accept', args=[u2_pending_follower.username])
        response = client.put(url)

        assert response.status_code == status.HTTP_200_OK
        assert (
            Subscription.objects.filter(
                follower=u2_pending_follower,
                follows_to=user2_closed,
                status=Subscription.ACCEPTED
            ).exists()
        )
    
    @pytest.mark.parametrize(
        ('who', 'whom'),
        (
            ('user2_closed', 'u2_accepted_follower'),
            ('user2_closed', 'u2_pending_follower')
        )
    )
    def test_reject_subscriprion(
        self,
        client,
        who,
        whom,
        user2_closed,
        u2_accepted_follower,
        u2_pending_follower
    ):
        who = vars().get(who)
        whom = vars().get(whom)

        client.force_authenticate(who)

        url = reverse('user-accept', args=[whom.username])
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not (
            Subscription.objects.filter(
                follower=whom,
                follows_to=who,
            ).exists()
        )
