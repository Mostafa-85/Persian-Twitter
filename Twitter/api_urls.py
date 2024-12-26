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
    path('follow/unfollow/<int:to_user_id>/', FollowUnfollowAPIView.as_view(), name='follow_unfollow'),
    path('user/<int:user_id>/connections/<str:connection_type>/', UserConnectionsAPIView.as_view(), name='user-connections'),
    path('create/post/',Create_Post.as_view(),name='post'),
    path('hashtag/<str:hashtag_name>/', HashtagPostsAPIView.as_view(), name='hashtag_posts'),
    path('search/hashtag/', SearchHashtagAPIView.as_view(), name='search_ha shtag'),
    path('post/<int:post_id>/',Crud_Post.as_view(),name='post_crud'),
    path('post/all/me/',PostsMe.as_view(),name='posts_me'),
    path("post/all/<int:user_id>/",PostAllUser.as_view(),name='post_all'),
    path('post/<int:post_id>/add_comment/', AddComment.as_view(), name='add_comment'),
    path('comments/<int:comment_id>/delete/', DeleteCommentAPIView.as_view(), name='delete-comment'),
    path('post/<int:post_id>/comments/', PostComments.as_view(), name='post_comments'),
    path('post/<int:post_id>/like/', LikePost.as_view(), name='like_post'),
    path('post/<int:post_id>/likes/', LikeCount.as_view(), name='like_count'),


]




