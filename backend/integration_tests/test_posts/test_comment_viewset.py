from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status


# TODO add query count
@pytest.mark.comments
@pytest.mark.django_db
class TestCommentViewSet:

    COMMENTS_FIELDS = {
        'id',
        'owner',
        'text',
    }

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('comment_owner', status.HTTP_204_NO_CONTENT)
        )
    )
    def test_delete_comment_permissions(
        self,
        user,
        expected_status,
        client,
        user1,
        user2,
        user2_posts
    ):
        comment = user2_posts[0]['comments'][0]
        comment_owner = comment.owner

        user = vars().get(user)

        client.force_authenticate(user)
        response = client.delete(reverse('comment-detail', args=[comment.id]))
        assert response.status_code == expected_status, (
            'only comment owner can delete it'
        )

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('comment_owner', status.HTTP_200_OK)
        )
    )
    def test_update_comment_permissions(
        self,
        user,
        expected_status,
        client,
        user1,
        user2,
        user2_posts
    ):
        comment = user2_posts[0]['comments'][0]
        comment_owner = comment.owner

        user = vars().get(user)

        client.force_authenticate(user)
        response = client.patch(reverse('comment-detail', args=[comment.id]))
        assert response.status_code == expected_status, (
            'only comment owner can delete it'
        )

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (   
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_201_CREATED),
            ('u2_pending_follower', status.HTTP_201_CREATED),
            ('u2_accepted_follower', status.HTTP_201_CREATED),
            ('user2', status.HTTP_201_CREATED),
        )
    )
    def test_create_comment_for_open_post(
        self, 
        user,
        expected_status,
        client, 
        user1, 
        user2,
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts
    ):
        user = vars().get(user)
        post = user2_posts[0]['post']

        client.force_authenticate(user)
        response = client.post(
            reverse('comment-list') + f'?post_id={post.id}',
            data={'text': 'text'}
        )
        assert response.status_code == expected_status
    
    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (   
            (None, status.HTTP_401_UNAUTHORIZED),
            ('user1', status.HTTP_403_FORBIDDEN),
            ('u2_pending_follower', status.HTTP_403_FORBIDDEN),
            ('u2_accepted_follower', status.HTTP_201_CREATED),
            ('user2_closed', status.HTTP_201_CREATED),
        )
    )
    def test_create_comment_for_closed_post(
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
        user = vars().get(user)
        post = user2_posts[0]['post']

        client.force_authenticate(user)
        response = client.post(
            reverse('comment-list') + f'?post_id={post.id}',
            data={'text': 'text'}
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        ('user', 'expected_status'),
        (   
            (None, status.HTTP_200_OK),
            ('user1', status.HTTP_200_OK),
            ('u2_pending_follower', status.HTTP_200_OK),
            ('u2_accepted_follower', status.HTTP_200_OK),
            ('user2', status.HTTP_200_OK),
        )
    )
    def test_get_comments_for_open_post(
        self, 
        user,
        expected_status,
        client, 
        user1, 
        user2,
        u2_pending_follower,
        u2_accepted_follower,
        user2_posts
    ):
        user = vars().get(user)
        post = user2_posts[0]['post']
        comments = user2_posts[0]['comments']

        client.force_authenticate(user)

        with mock.patch(
            'speshalgram.posts.views.CommentViewSet.pagination_class',
            None
        ):
            response = client.get(
                reverse('comment-list') + f'?post_id={post.id}',
            )
            assert response.status_code == expected_status

            if response.status_code == status.HTTP_200_OK:
                comments = sorted(
                    comments, 
                    key=lambda c: (c.date_created, c.id), 
                    reverse=True
                )
                
                assert len(response.json()) == len(comments)
                for ret_comment, comment in zip(response.json(), comments):
                    assert ret_comment.keys() == self.COMMENTS_FIELDS
                    assert ret_comment['id'] == comment.id

    
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
    def test_get_comments_for_closed_post(
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
        user = vars().get(user)
        post = user2_posts[0]['post']
        comments = user2_posts[0]['comments']

        client.force_authenticate(user)

        with mock.patch(
            'speshalgram.posts.views.CommentViewSet.pagination_class',
            None
        ):
            response = client.get(
                reverse('comment-list') + f'?post_id={post.id}',
            )
            assert response.status_code == expected_status

            if response.status_code == status.HTTP_200_OK:
                comments = sorted(
                    comments, 
                    key=lambda c: (c.date_created, c.id), 
                    reverse=True
                )
                
                assert len(response.json()) == len(comments)
                for ret_comment, comment in zip(response.json(), comments):
                    assert ret_comment.keys() == self.COMMENTS_FIELDS
                    assert ret_comment['id'] == comment.id
