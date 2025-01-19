from django.urls import path

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/',RegisterAPIView.as_view(),name='register'),
    path('login/', CustomLoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("logout/",LogoutAPIView.as_view(),name='logout'),
    path('user/profile/',UserProfileAPIView.as_view(),name='user_profile'),
    path('user/<int:user_id>/', UserProfileDetailAPIView.as_view(), name='user-profile-detail'),
    path('follow-request_or_cancel/<int:to_user_id>/', FollowRequestAPIView.as_view(), name='follow-request'),
    path('follow-requests/', FollowRequestListAPIView.as_view(), name='follow-request-list'),
    path('follow-requests/<int:follow_request_id>/<str:action>/', FollowRequestActionAPIView.as_view(), name='follow-request-action'),
    path('follow/unfollow/<int:to_user_id>/', FollowUnfollowAPIView.as_view(), name='follow_unfollow'),
    path('followers_me/', FollowersListAPIView.as_view(), name='followers-list'),
    path('followings_me/', FollowingsListAPIView.as_view(), name='followings-list'),
    path('user/<int:user_id>/connections/<str:connection_type>/', UserConnectionsAPIView.as_view(), name='user-connections'),
    path('post/create/',Create_Post.as_view(),name='post'),
    path('hashtag/<str:hashtag_name>/', HashtagPostsAPIView.as_view(), name='hashtag_posts'),
    path('search/hashtag/', SearchHashtagAPIView.as_view(), name='search_ha shtag'),
    path('search/user', SearchUserAPIView.as_view(), name='search_user'),
    path('post/<int:post_id>/',Edit_Post.as_view(),name='post_crud'),
    path('post/all/me/',PostsMe.as_view(),name='posts_me'),
    path("post/all/<int:user_id>/",PostAllUser.as_view(),name='post_all'),
    path('post/<int:post_id>/add_comment/', AddComment.as_view(), name='add_comment'),
    path('post/comments/<int:comment_id>/delete/', DeleteCommentAPIView.as_view(), name='delete-comment'),
    path('post/<int:post_id>/comments/', PostComments.as_view(), name='post_comments'),
    path('post/<int:post_id>/like/', LikePost.as_view(), name='like_post'),
    path('post/<int:post_id>/likes/', LikeCount.as_view(), name='like_count'),
    path('popular/users/',SuggestedUsers.as_view(), name='suggested_users'),
    path('popular/posts/',PopularPosts.as_view(), name='popular_posts'),
    path('notifications/',NotificationListView.as_view(), name='notifications'),

]




