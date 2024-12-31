from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Connection, User, Post, Like, Comment, Hashtag, ViewPost
from .Serializer import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import LimitOffsetPagination
import re
from drf_yasg import openapi


def extract_hashtags(content):
    return re.findall(r"#(\w+)", content)  # جستجوی کلمات با # در متن



class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        request_body=UserRejisterDTO
    )
    def post(self, request):

        refresh_token = request.data.get("refresh_token")

        if refresh_token:
            try:
                # تلاش برای احراز هویت با توکن رفرش
                refresh = RefreshToken(refresh_token)
                user = User.objects.get(id=refresh.payload['user_id'])  # یا هر روشی برای پیدا کردن کاربر بر اساس توکن
                if user:
                    # کاربر یافت شد و توکن رفرش معتبر است
                    access_token = str(refresh.access_token)  # توکن اکسس جدید
                    return Response({
                        'detail': 'کاربر قبلا ثبت نام کرده است!!',
                        'access': access_token,
                        'refresh': str(refresh),
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'detail': ''
                }, status=status.HTTP_400_BAD_REQUEST)


        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if re.search(r'[\u0600-\u06FF]', username):
            return Response(
                {"error": "نام کاربری باید با حروف انگلیسی باشد!!!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response({"error": "این نام کاربری از قبل ثبت شده!!!"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        user.is_superuser=False
        user.is_staff=False
        user.save()
        return Response({
            "message": "با موفقیت ثبت نام شد.",
            "login_url":"api/login/"

                         },
                        status=status.HTTP_201_CREATED)


class CustomLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginDTO
    )
    def post(self, request):

        # بررسی که آیا کاربر قبلاً لاگین کرده است و توکن رفرش معتبر است
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                # تلاش برای احراز هویت با توکن رفرش
                refresh = RefreshToken(refresh_token)
                user = User.objects.get(id=refresh.payload['user_id'])  # یا هر روشی برای پیدا کردن کاربر بر اساس توکن
                if user:
                    # کاربر یافت شد و توکن رفرش معتبر است
                    access_token = str(refresh.access_token)  # توکن اکسس جدید
                    return Response({
                        'detail': 'کاربر درحال حاضر لاگین است!!',
                        'access': access_token,
                        'refresh': str(refresh),
                    }, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                return Response({
                    'detail': ''
                }, status=status.HTTP_400_BAD_REQUEST)


        # گرفتن نام کاربری و رمز عبور از درخواست
        username = request.data.get("username")
        password = request.data.get("password")

        # بررسی اعتبار نام کاربری و رمز عبور
        user = authenticate(username=username, password=password)

        if user is not None:
            # اگر کاربر پیدا شد، توکن را صادر کن
            refresh=RefreshToken.for_user(user)
            access_token=str(refresh.access_token)  # اینجا به درستی از refresh.access_token استفاده می‌کنیم

            # ارسال توکن‌ها به کاربر
            return Response({
                'access': access_token,
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'نام کاربری یا رمز عبور نامعتبر است!!!'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogoutDTO
    )
    def post(self, request):
        # گرفتن توکن رفرش از هدر درخواست
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()  # بلک‌لیست کردن توکن رفرش
            return Response({"message": "کاربر لاگ اوت شد!!!"}, status=200)
        except Exception as e:
            return Response({"detail": "Invalid token or other error"}, status=400)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # برای آپلود عکس پروفایل

    def get(self, request):
        user = request.user  # کاربر لاگین شده را می‌گیریم

        try:
            # پیدا کردن پروفایل کاربر
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        # یافتن لیست فالورها و فالوینگ‌ها
        followers = user_profile.followers.all().values_list('from_user__user__username', flat=True)
        following = user_profile.following.all().values_list('to_user__user__username', flat=True)

        # یافتن لیست پست‌های کاربر
        user_posts = Post.objects.filter(user=user_profile).order_by('-created_at').values('id', 'title', 'content', 'created_at')

        # برگرداندن اطلاعات پروفایل کاربر به همراه فالورها، فالوینگ‌ها و پست‌ها
        return Response({
            "id":user_profile.id,
            "username": user.username,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user.email,
            "bio": user_profile.bio,
            "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None,
            "type": user_profile.type,
            "followers": list(followers),
            "following": list(following),
            "posts": list(user_posts)
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserProfileDTO
    )
    def put(self, request):
        user = request.user  # کاربر لاگین شده را می‌گیریم

        try:
            # پیدا کردن پروفایل کاربر
            user_profile = UserProfile.objects.get(user=user)

        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=404)

        # دریافت اطلاعات جدید از درخواست
        first_name = request.data.get('first_name', user_profile.first_name)
        last_name = request.data.get('last_name', user_profile.last_name)
        bio = request.data.get('bio', user_profile.bio)
        type = request.data.get('type', user_profile.type)
        profile_picture = request.FILES.get('profile_picture', user_profile.profile_picture)


        # به‌روزرسانی پروفایل
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.bio = bio
        user_profile.type = type

        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.save()

        return Response({
            "message": "پروفایل با موفقیت به‌روزرسانی شد.",
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "bio": user_profile.bio,
            "type": user_profile.type,
            "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None
        }, status=status.HTTP_200_OK)


class UserProfileDetailAPIView(APIView):
    def get(self, request, user_id):
        try:
            # یافتن کاربر بر اساس ID
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "کاربر مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # یافتن پروفایل کاربر
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        # دریافت همه پست‌های کاربر
        posts = Post.objects.filter(user=user_profile).order_by('-created_at')
        serialized_posts = CradPostSerializer(posts, many=True).data

        # دریافت لیست فالوورها
        followers = Connection.objects.filter(to_user=user_profile).select_related('from_user')
        follower_data = [
            {
                "id": connection.from_user.id,
                "username": connection.from_user.user.username,
                "profile_picture": connection.from_user.profile_picture.url if connection.from_user.profile_picture else None
            }
            for connection in followers
        ]

        # دریافت لیست فالوینگ‌ها
        following = Connection.objects.filter(from_user=user_profile).select_related('to_user')
        following_data = [
            {
                "id": connection.to_user.id,
                "username": connection.to_user.user.username,
                "profile_picture": connection.to_user.profile_picture.url if connection.to_user.profile_picture else None
            }
            for connection in following
        ]

        # ارسال اطلاعات پروفایل
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user.email,
            "bio": user_profile.bio,
            "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None,
            "type": user_profile.type,
            "posts": serialized_posts,
            "followers": follower_data,
            "following": following_data,
        }, status=status.HTTP_200_OK)


class FollowUnfollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        """عملیات فالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "این یوزر آدی یافت نشد!!"}, status=status.HTTP_404_NOT_FOUND)

        if from_user == to_user:
            return Response({"error": "شما نمی توانید خودتون رو فالو کنید!!"}, status=status.HTTP_400_BAD_REQUEST)

        connection, created = Connection.objects.get_or_create(from_user=from_user, to_user=to_user)

        if created:
            return Response({"message": "کاربر فالو شد!!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "شما قبلا این کاربر رو فالو کردید!!"}, status=status.HTTP_200_OK)

    def delete(self, request, to_user_id):
        """عملیات آنفالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربری با این یوزر ایدی یافت نشد!!"}, status=status.HTTP_404_NOT_FOUND)

        try:
            connection = Connection.objects.get(from_user=from_user, to_user=to_user)
            connection.delete()
            return Response({"message": "انفالو شد!!"}, status=status.HTTP_204_NO_CONTENT)
        except Connection.DoesNotExist:
            return Response({"error": "شما هنوز کاربر را فالو نکردید!!"}, status=status.HTTP_400_BAD_REQUEST)


class UserConnectionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, connection_type):
        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        if connection_type == "followers":
            connections = Connection.objects.filter(to_user=user_profile).values_list('from_user', flat=True)
        elif connection_type == "following":
            connections = Connection.objects.filter(from_user=user_profile).values_list('to_user', flat=True)
        else:
            return Response({"error": "نوع اتصال نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        profiles = UserProfile.objects.filter(id__in=connections)
        data = UserProfileSerializer(profiles, many=True).data

        return Response({connection_type: data}, status=status.HTTP_200_OK)


class Create_Post(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        request_body=PostDTO,
        manual_parameters=[
            openapi.Parameter(
                'post_picture',
                openapi.IN_FORM,
                description="تصویر پست",
                type=openapi.TYPE_FILE,  # نوع داده برای فایل
                required=False  # اختیاری بودن فیلد
            )
        ]
    )
    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "کسی با این نام کاربری وجود ندارد"}, status=status.HTTP_404_NOT_FOUND)

        title = request.data.get('title')
        content = request.data.get('content')
        post_picture = request.FILES.get('post_picture')

        if not title or not content:
            return Response({"error": "عنوان و محتوا را خالی گذاشتید!!!"}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.create(user=user_profile, title=title, content=content, post_picture=post_picture)
        post.save()


        # استخراج و ذخیره هشتگ‌ها
        hashtags = extract_hashtags(content)
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())  # ذخیره یا پیدا کردن هشتگ
            post.hashtags.add(hashtag)

        serialized_post = CreatePostSerializer(post).data
        return Response({"message": "پست توسط کاربر ایجاد شد", "post": serialized_post}, status=status.HTTP_201_CREATED)


class  Edit_Post(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post = Post.objects.get(id=post_id)
            if user_profile != post.user:
                return Response({"error": "شما مالک این پست نیستید"}, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({"error": "هیچ پستی با این پست آیدی وجود ندارد!!!"}, status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response({"message": "پست حذف شد!!"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=EditPostDTO
    )
    def put(self, request, post_id):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post = Post.objects.get(id=post_id)
            if user_profile != post.user:
                return Response({"error": "شما مالک این پست نیستید"}, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({"error": "هیچ پستی با این پست آیدی وجود ندارد!!!"}, status=status.HTTP_404_NOT_FOUND)

        post.content = request.data.get('content', post.content)
        post.save()
        return Response({"message": "پست با موفقیت بروزرسانی شد!"}, status=status.HTTP_200_OK)

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "پستی یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        view, created = ViewPost.objects.get_or_create(from_user=request.user.userprofile, post=post)

        serialized_post = CradPostSerializer(post).data
        return Response({"post": serialized_post}, status=status.HTTP_200_OK)


class PostsMe(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر یافت نشد !!!"}, status=status.HTTP_404_NOT_FOUND)

        user_posts = Post.objects.filter(user=user_profile).order_by('-created_at')
        serialized_posts = CradPostSerializer(user_posts, many=True).data

        return Response({"message": "همه پست‌های شما", "posts": serialized_posts}, status=status.HTTP_200_OK)


class PostAllUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,user_id):
        try:
            user_profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر یافت نشد !!!"}, status=status.HTTP_404_NOT_FOUND)

        # فیلتر کردن پست‌های کاربر
        user_posts = Post.objects.filter(user=user_profile)

        # سریالایز کردن داده‌ها
        serialized_posts = CradPostSerializer(user_posts, many=True).data

        return Response({"posts": serialized_posts}, status=status.HTTP_200_OK)


class HashtagPostsAPIView(APIView):
    def get(self, request, hashtag_name):
        try:
            hashtag = Hashtag.objects.get(name=hashtag_name.lower())
        except Hashtag.DoesNotExist:
            return Response({"error": "هشتگ یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        posts = Post.objects.filter(hashtags=hashtag).order_by('-created_at')
        serialized_posts = CradPostSerializer(posts, many=True).data

        return Response({
            "hashtag": hashtag.name,
            "posts": serialized_posts
        }, status=status.HTTP_200_OK)


class SearchHashtagAPIView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'query',  # نام پارامتر
                openapi.IN_QUERY,  # مشخص کردن نوع پارامتر (در اینجا query)
                description="هشتگ مورد نظر برای جستجو",
                type=openapi.TYPE_STRING,  # نوع داده
                required=True  # اجباری بودن پارامتر
            )
        ]
    )
    def get(self, request,):
        query = request.query_params.get('query')  # دریافت پارامتر query از query string

        if not query:
            return Response({"error": "هشتگ مورد نظر را وارد کنید."}, status=status.HTTP_400_BAD_REQUEST)

        # جستجوی پست‌هایی که شامل هشتگ مورد نظر هستند
        posts = Post.objects.filter(hashtags__name__icontains=query)

        if not posts.exists():
            return Response({"message": "هیچ پستی با این هشتگ یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        serialized_posts = CradPostSerializer(posts, many=True).data
        return Response({"message": f"پست‌های مرتبط با هشتگ '{query}'", "posts": serialized_posts}, status=status.HTTP_200_OK)


class AddComment(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PostCommentsDTO
            )
    def post(self, request, post_id):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post = Post.objects.get(id=post_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({"error": "پست یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content')
        parent_id = request.data.get('parent', None)

        if not content:
            return Response({"error": "محتوای کامنت نمی‌تواند خالی باشد."}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return Response({"error": "کامنت والد یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        comment = Comment.objects.create(post=post, user=user_profile, content=content, parent=parent)
        serialized_comment = CommentSerializer(comment).data

        return Response({"message": "کامنت با موفقیت اضافه شد.", "comment": serialized_comment}, status=status.HTTP_201_CREATED)


class PostComments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "پست یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)

        # دریافت کامنت‌های اصلی (بدون والد)
        comments = Comment.objects.filter(post=post, parent=None).order_by('-created_at')
        serialized_comments = CommentSerializer(comments, many=True).data

        return Response({"comments": serialized_comments}, status=status.HTTP_200_OK)


class DeleteCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user_profile = request.user.userprofile  # فرض بر این است که UserProfile مرتبط با User است

        # بررسی اینکه کاربر صاحب کامنت یا صاحب پست است
        if comment.user == user_profile or comment.post.user == user_profile:
            comment.delete()
            return Response({"message": "کامنت با موفقیت حذف شد."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "شما اجازه حذف این کامنت را ندارید."}, status=status.HTTP_403_FORBIDDEN)


class LikePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post = Post.objects.get(id=post_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({"error": "پست یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=user_profile)
        if not created:
            like.delete()
            return Response({"message": "پست با موفقیت آنلایک شد."}, status=status.HTTP_200_OK)

        return Response({"message": "پست با موفقیت لایک شد."}, status=status.HTTP_201_CREATED)


class LikeCount(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "پست یافت نشد!!!"}, status=status.HTTP_404_NOT_FOUND)

        A='DS'
        like_count = post.likes.count()
        return Response({"likes": like_count}, status=status.HTTP_200_OK)















