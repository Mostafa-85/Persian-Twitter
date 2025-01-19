from django.db.models import Count
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Twitter.models import *
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

class ExplorePagination(PageNumberPagination):
    page_size = 10  # تعداد آیتم‌های هر صفحه
    page_size_query_param = 'page_size'
    max_page_size = 50  # حداکثر تعداد آیتم‌ها در هر صفحه


class Explore(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = ExplorePagination
    def get(self, request):

        posts = Post.objects.annotate(
            like_count=Count('likes'),
            comment_count=Count('comments'),
            view_count= Count('views')
        ).order_by('-like_count', '-comment_count', '-view_count')

        paginator = self.pagination_class()
        posts = paginator.paginate_queryset(posts, request)

        results = []
        for post in posts:
            # بررسی وجود فایل تصویر
            post_picture_url = post.post_picture.url if post.post_picture and post.post_picture.name else None

            results.append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'views_count': post.views_count,
                'post_picture': post_picture_url,  # تصویر فقط در صورت وجود
                'user': post.user.user.username,
                'user_id':post.user.id,
                'created_at': post.created_at,
            })
        return paginator.get_paginated_response(results)


class HotHashtag(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        hashtags = Hashtag.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count')


        hashtags = hashtags[:10]

        if not hashtags:
            return Response({"error": "هشتگ یافjت نشد."}, status=status.HTTP_404_NOT_FOUND)

        results = [
            {
                'name': hashtag.name,
                'post_count': hashtag.post_count
            }
            for hashtag in hashtags
        ]

        return Response(results)



