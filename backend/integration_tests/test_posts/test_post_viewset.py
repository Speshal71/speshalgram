from unittest import mock

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from speshalgram.posts.models import Post


# TODO add query count
@pytest.mark.posts
@pytest.mark.django_db
class TestPostViewSet:

    POSTS_LIST_FIELDS = {
        'id',
        'owner',
        'picture',
        'description',
        'nlikes',
        'preview_comments',
        'is_liked_by_me',
    }

    POST_DETAIL_FIELDS = POSTS_LIST_FIELDS - {'preview_comments'}

    FEED_FIELDS = POSTS_LIST_FIELDS

    PREVIEW_COMMENTS_FIELDS = {
        'id',
        'owner',
        'text',
    }

    @pytest.mark.parametrize(
        ('user',),
        (
            (None,),
            ('user1',),
            ('u2_accepted_follower',),
            ('user2',),
        )
    )
    def test_open_user_posts(
        self, 
        client, 
        user, 
        user1, 
        user2, 
        u2_accepted_follower
    ):
        user = vars().get(user)

        client.force_authenticate(user)
        response = client.get(
            reverse('post-list') + f'?username={user2.username}'
        )

        assert response.status_code == status.HTTP_200_OK

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
    def test_closed_user_posts(
        self, 
        client, 
        user,
        expected_status,
        user1, 
        user2_closed, 
        u2_pending_follower,
        u2_accepted_follower,
    ):
        user = vars().get(user)

        client.force_authenticate(user)
        response = client.get(
            reverse('post-list') + f'?username={user2_closed.username}'
        )

        assert response.status_code == expected_status
    
    def test_user_posts_content(
        self,
        client,
        user1,
        user2,
        user2_posts
    ):
        user = user1
        client.force_authenticate(user)
        
        with mock.patch(
            'speshalgram.posts.views.PostViewSet.pagination_class',
            None
        ):
            response = client.get(
                reverse('post-list') + f'?username={user2.username}'
            )

            assert response.status_code == status.HTTP_200_OK
            
            response_json = response.json()
            assert len(response_json) == len(user2_posts)

            for returned_post, post in zip(
                response_json, 
                sorted(
                    user2_posts,
                    key=lambda p: p['post'].date_created,
                    reverse=True
                )
            ):
                assert returned_post.keys() == self.POSTS_LIST_FIELDS
                assert returned_post['id'] == post['post'].id
                assert returned_post['nlikes'] == len(post['likes'])
                assert returned_post['is_liked_by_me'] == any(
                    like.owner_id == user.id for like in post['likes']
                )

                expected_preview_comments = sorted(
                    post['comments'],
                    key=lambda c: (c.date_created, c.id),
                )[-settings.NUM_OF_PREVIEW_COMMENTS:]
                
                assert (
                    len(returned_post['preview_comments']) == 
                    len(expected_preview_comments)
                )
                for ret_comment, comment in zip(
                    returned_post['preview_comments'], 
                    expected_preview_comments
                ):
                    assert ret_comment.keys() == self.PREVIEW_COMMENTS_FIELDS
                    assert ret_comment['id'] == comment.id
    
    def test_user_feed_content(
        self,
        client,
        user2,
        user2_posts,
        u2_accepted_follower_who_liked_his_posts,
    ):
        user = u2_accepted_follower_who_liked_his_posts
        client.force_authenticate(user)
        
        with mock.patch(
            'speshalgram.posts.views.PostViewSet.pagination_class',
            None
        ):
            response = client.get(reverse('post-feed'))

            assert response.status_code == status.HTTP_200_OK
            
            response_json = response.json()
            assert len(response_json) == len(user2_posts)

            for returned_post, post in zip(
                response_json, 
                sorted(
                    user2_posts,
                    key=lambda p: (p['post'].date_created, p['post'].id),
                    reverse=True
                )
            ):
                assert returned_post.keys() == self.FEED_FIELDS
                assert returned_post['id'] == post['post'].id
                assert returned_post['nlikes'] == len(post['likes'])
                assert returned_post['is_liked_by_me'] == True

                expected_preview_comments = sorted(
                    post['comments'],
                    key=lambda c: (c.date_created, c.id),
                )[-settings.NUM_OF_PREVIEW_COMMENTS:]
                
                assert (
                    len(returned_post['preview_comments']) == 
                    len(expected_preview_comments)
                )
                for ret_comment, comment in zip(
                    returned_post['preview_comments'], 
                    expected_preview_comments
                ):
                    assert ret_comment.keys() == self.PREVIEW_COMMENTS_FIELDS
                    assert ret_comment['id'] == comment.id

    def test_user_no_feed(
        self,
        client,
        u2_pending_follower,
        user2,
        user2_posts
    ):
        client.force_authenticate(u2_pending_follower)
        
        with mock.patch(
            'speshalgram.posts.views.PostViewSet.pagination_class',
            None
        ):
            response = client.get(reverse('post-feed'))

            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()) == 0
    
    @pytest.mark.parametrize(
        ('user',),
        (
            (None,),
            ('user1',),
            ('u2_accepted_follower',),
            ('user2',),
        )
    )
    def test_retrieve_open_user_post(
        self, 
        client, 
        user, 
        user1, 
        user2, 
        u2_accepted_follower,
        user2_posts
    ):
        user = vars().get(user)
        post = user2_posts[0]

        client.force_authenticate(user)
        response = client.get(reverse('post-detail', args=[post['post'].id]))

        assert response.status_code == status.HTTP_200_OK
    
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
    def test_retrieve_closed_user_post(
        self, 
        client, 
        user,
        expected_status,
        user1, 
        user2_closed, 
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts,
    ):
        user = vars().get(user)
        post = user2_posts[0]

        client.force_authenticate(user)
        response = client.get(reverse('post-detail', args=[post['post'].id]))

        assert response.status_code == expected_status

    def test_retrieve_user_post(
        self, 
        client,
        user2,
        user2_posts
    ):
        post = user2_posts[0]

        response = client.get(reverse('post-detail', args=[post['post'].id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == self.POST_DETAIL_FIELDS
        assert response.json()['id'] == post['post'].id
        assert response.json()['nlikes'] == len(post['likes'])
        assert response.json()['is_liked_by_me'] == False

    def test_create_post(self, client, user1, test_gif):
        assert Post.objects.filter(owner=user1).count() == 0

        client.force_authenticate(user1)
        response = client.post(
            reverse('post-list'),
            data={
                'description': 'desc',
                'picture': SimpleUploadedFile(
                    'test.gif', 
                    test_gif, 
                    content_type='image/gif'
                ),
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(owner=user1).count() == 1
        assert response.json()['owner']['username'] == user1.username
        assert response.json()['description'] == 'desc' 
    
    def test_update_post(
        self,
        client,
        user1,
        user2,
        user2_posts,
        test_gif
    ):
        post = user2_posts[0]['post']

        client.force_authenticate(user1)
        response = client.patch(
            reverse('post-detail', args=[post.id]),
            data={'description': 'some new desc'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            'only post creator can update it'
        )

        client.force_authenticate(user2)

        response = client.patch(
            reverse('post-detail', args=[post.id]),
            data={
                'picture': SimpleUploadedFile(
                    'test.gif', 
                    test_gif, 
                    content_type='image/gif'
                ),
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            'it\'s forbidden to update image'
        )

        response = client.patch(
            reverse('post-detail', args=[post.id]),
            data={'description': 'some new desc'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['description'] == 'some new desc'

    def test_delete_post(
        self,
        client,
        user1,
        user2,
        user2_posts,
    ):
        post = user2_posts[0]['post']

        client.force_authenticate(user1)
        response = client.delete(reverse('post-detail', args=[post.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            'only post creator can delete it'
        )
        assert Post.objects.filter(owner=user2).count() == len(user2_posts)

        client.force_authenticate(user2)
        response = client.delete(reverse('post-detail', args=[post.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            'only post creator can update it'
        )
        assert Post.objects.filter(owner=user2).count() == len(user2_posts) - 1
