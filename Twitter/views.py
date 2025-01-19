from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .Serializer import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
import re
from drf_yasg import openapi
from django.db.models import Q ,Count



def extract_hashtags(content):
    return re.findall(r"#(\w+)", content)  # جستجوی کلمات با # در متن


class UserSearchPagination(PageNumberPagination):
    page_size = 10  # تعداد آیتم‌های هر صفحه
    page_size_query_param = 'page_size'
    max_page_size = 50  # حداکثر تعداد آیتم‌ها در هر صفحه


class SuggestedUsersPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 25


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        request_body=UserRejisterDTO
    )
    def post(self, request):

        refresh_token = request.data.get("refresh_token")

        if refresh_token:
            try:

                refresh = RefreshToken(refresh_token)
                user = User.objects.get(id=refresh.payload['user_id'])
                if user:

                    access_token = str(refresh.access_token)
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



        username = request.data.get("username")
        password = request.data.get("password")


        user = authenticate(username=username, password=password)

        if user is not None:

            refresh=RefreshToken.for_user(user)
            access_token=str(refresh.access_token)

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

        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "کاربر لاگ اوت شد!!!"}, status=200)
        except Exception as e:
            return Response({"detail": "Invalid token or other error"}, status=400)


class SearchUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q',  # نام پارامتر
                openapi.IN_QUERY,  # مشخص کردن نوع پارامتر (در اینجا query)
                description="یوزر، یا نام مورد نظر برای جستجو",
                type=openapi.TYPE_STRING,  # نوع داده
                required=True  # اجباری بودن پارامتر
            )
        ]
    )
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"error": "لطفاً یک عبارت جستجو وارد کنید."}, status=400)


        current_user = request.user

        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=current_user.id)

        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)

        results = [
            {
                "id": user.id,
                "username": user.username,
                "profile_picture": user.userprofile.profile_picture.url if hasattr(user,
                                                                                   'userprofile') and user.userprofile.profile_picture else None
            }
            for user in paginated_users
        ]

        return paginator.get_paginated_response(results)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # برای آپلود عکس پروفایل

    def get(self, request):
        user = request.user

        try:

            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


        followers = user_profile.followers.all().values_list('from_user__user__username', flat=True)
        following = user_profile.following.all().values_list('to_user__user__username', flat=True)


        user_posts = Post.objects.filter(user=user_profile).order_by('-created_at').values('id', 'title', 'content', 'created_at')

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
        user = request.user

        try:

            user_profile = UserProfile.objects.get(user=user)

        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=404)


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
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "کاربر مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "پروفایل کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


        is_private = user_profile.type


        is_follower = Connection.objects.filter(from_user=request.user.userprofile, to_user=user_profile).exists()


        followers_count = Connection.objects.filter(to_user=user_profile).count()
        following_count = Connection.objects.filter(from_user=user_profile).count()


        if is_private and not is_follower:
            return Response({
                "id": user.id,
                "username": user.username,
                "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None,
                "is_private": True,
                "followers_count": followers_count,
                "following_count": following_count,
                "message": "این حساب خصوصی است. شما دسترسی کامل به اطلاعات این کاربر ندارید."
            }, status=status.HTTP_200_OK)

        # اگر حساب عمومی است یا کاربر فالوئر است
        followers = Connection.objects.filter(to_user=user_profile).select_related('from_user')
        following = Connection.objects.filter(from_user=user_profile).select_related('to_user')

        follower_data = [
            {
                "id": connection.from_user.id,
                "username": connection.from_user.user.username,
                "profile_picture": connection.from_user.profile_picture.url if connection.from_user.profile_picture else None
            }
            for connection in followers
        ]

        following_data = [
            {
                "id": connection.to_user.id,
                "username": connection.to_user.user.username,
                "profile_picture": connection.to_user.profile_picture.url if connection.to_user.profile_picture else None
            }
            for connection in following
        ]

        posts = Post.objects.filter(user=user_profile).order_by('-created_at') if is_follower or not is_private else []
        serialized_posts = CradPostSerializer(posts, many=True).data

        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name,
            "email": user.email,
            "bio": user_profile.bio,
            "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None,
            "type": user_profile.type,
            "is_private": is_private,
            "followers_count": followers_count,
            "following_count": following_count,
            "followers": follower_data,
            "following": following_data,
            "posts": serialized_posts
        }, status=status.HTTP_200_OK)


class FollowRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        """ارسال درخواست فالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "این یوزر آیدی یافت نشد!"}, status=status.HTTP_404_NOT_FOUND)

        if from_user == to_user:
            return Response({"error": "شما نمی‌توانید خودتان را فالو کنید!"}, status=status.HTTP_400_BAD_REQUEST)


        if Connection.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"message": "شما قبلاً این کاربر را فالو کرده‌اید!"}, status=status.HTTP_200_OK)

        if to_user.type:  # پیج خصوصی
            follow_request, created = FollowRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
            if created:
                Notification.objects.create(
                    user=to_user,
                    actor=from_user,
                    status="follow_request",  # استفاده از status به جای action_type
                    target="FollowRequest",  # نام شیء هدف
                    target_id=follow_request.id,  # شناسه شیء هدف
                    message=f"{from_user.user.username} درخواست فالو برای شما ارسال کرد."
                )
                return Response({"message": "درخواست فالو ارسال شد!"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "شما قبلاً درخواست فالو ارسال کرده‌اید!"}, status=status.HTTP_200_OK)
        else:  # پیج عمومی
            return Response({"error": "فقط درخواست‌های فالو برای صفحات خصوصی ارسال می‌شود."}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, to_user_id):
        """حذف درخواست فالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "این یوزر آدی یافت نشد!!"}, status=status.HTTP_404_NOT_FOUND)

        try:
            follow_request = FollowRequest.objects.get(from_user=from_user, to_user=to_user)
            follow_request.delete()
            return Response({"message": "درخواست فالو با موفقیت حذف شد!!"}, status=status.HTTP_200_OK)
        except FollowRequest.DoesNotExist:
            return Response({"error": "درخواستی برای این کاربر یافت نشد!"}, status=status.HTTP_404_NOT_FOUND)


class FollowUnfollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        """عملیات فالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "این یوزر آیدی یافت نشد!"}, status=status.HTTP_404_NOT_FOUND)

        if from_user == to_user:
            return Response({"error": "شما نمی‌توانید خودتان را فالو کنید!"}, status=status.HTTP_400_BAD_REQUEST)


        if Connection.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"message": "شما قبلاً این کاربر را فالو کرده‌اید!"}, status=status.HTTP_200_OK)

        if to_user.type:
            return Response({"error": "نمی‌توانید صفحات خصوصی را مستقیماً فالو کنید! درخواست فالو ارسال کنید."},
                            status=status.HTTP_403_FORBIDDEN)

        connection, created = Connection.objects.get_or_create(from_user=from_user, to_user=to_user)
        if created:
            return Response({"message": "کاربر با موفقیت فالو شد!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "شما قبلاً این کاربر را فالو کرده‌اید!"}, status=status.HTTP_200_OK)
    def delete(self, request, to_user_id):
        """عملیات آنفالو"""
        from_user = request.user.userprofile
        try:
            to_user = UserProfile.objects.get(id=to_user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "این یوزر آیدی یافت نشد!"}, status=status.HTTP_404_NOT_FOUND)

        try:
            connection = Connection.objects.get(from_user=from_user, to_user=to_user)
            connection.delete()
            return Response({"message": "کاربر با موفقیت آنفالو شد!"}, status=status.HTTP_200_OK)
        except Connection.DoesNotExist:
            return Response({"error": "شما این کاربر را فالو نکرده‌اید!"}, status=status.HTTP_400_BAD_REQUEST)


class FollowRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """نمایش درخواست‌های فالو دریافتی"""
        user_profile = request.user.userprofile
        follow_requests = FollowRequest.objects.filter(to_user=user_profile, status='pending')

        serializer = FollowRequestSerializer(follow_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowRequestActionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, follow_request_id, action):
        """قبول یا رد درخواست فالو"""
        user_profile = request.user.userprofile

        try:
            follow_request = FollowRequest.objects.get(id=follow_request_id, to_user=user_profile, status='pending')
        except FollowRequest.DoesNotExist:
            return Response({"error": "درخواست فالو یافت نشد یا قبلاً مدیریت شده است."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            follow_request.status = 'accepted'
            follow_request.save()

            Connection.objects.get_or_create(from_user=follow_request.from_user, to_user=user_profile)
            follow_request.delete()

            return Response({"message": "درخواست فالو قبول شد."}, status=status.HTTP_200_OK)
        elif action == 'reject':
            follow_request.status = 'rejected'
            follow_request.save()
            follow_request.delete()
            return Response({"message": "درخواست فالو رد شد."}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "عملیات نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)


class FollowersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """نمایش لیست فالورها"""
        user_profile = request.user.userprofile
        followers_connections = Connection.objects.filter(to_user=user_profile)

        followers = [connection.from_user for connection in followers_connections]
        serializer = UserProfileSerializer(followers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """نمایش لیست فالوینگ‌ها"""
        user_profile = request.user.userprofile
        followings_connections = Connection.objects.filter(from_user=user_profile)
        followings = [connection.to_user for connection in followings_connections]

        serializer = UserProfileSerializer(followings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                required=False
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
            return Response({"error": "پست یافت نشد"}, status=status.HTTP_404_NOT_FOUND)


        if post.user.type:  # اگر حساب خصوصی است
            # بررسی وضعیت فالوئینگ
            is_follower = Connection.objects.filter(from_user=request.user.userprofile, to_user=post.user).exists()
            if not is_follower:
                return Response({"error": "شما اجازه مشاهده این پست را ندارید."}, status=status.HTTP_403_FORBIDDEN)


        # ثبت مشاهده پست
        view, created = ViewPost.objects.get_or_create(from_user=request.user.userprofile, post=post)

        # سریالایز کردن داده‌ها
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

    def get(self, request, user_id):
        try:
            user_profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "کاربر یافت نشد !!!"}, status=status.HTTP_404_NOT_FOUND)


        if user_profile.type:

            is_follower = Connection.objects.filter(from_user=request.user.userprofile, to_user=user_profile).exists()
            if not is_follower:
                return Response({"error": "شما اجازه دسترسی به پست‌های این کاربر را ندارید."}, status=status.HTTP_403_FORBIDDEN)


        user_posts = Post.objects.filter(user=user_profile)


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
        Notification.objects.create(
            user=post.user,
            action_user=user_profile,
            action_type="comment",
            target_object=comment,
            message=f"{user_profile.user.username} کامنت گذاشت روی پست شما."
        )
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
        user_profile = request.user.userprofile

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

        if post.user != user_profile:  #
            Notification.objects.create(
                user=post.user,
                action_user=user_profile,
                action_type="like",
                target_object=post,
                message=f"{user_profile.user.username} لایک کرد پست شما را."
            )

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


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.userprofile
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationsSerializer(notifications, many=True)
        return Response({
            "count": notifications.count(),
            "notifications": serializer.data
        })


class SuggestedUsers(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = SuggestedUsersPagination

    def get(self, request):
        users = UserProfile.objects.annotate(
            follower_count=Count('followers')
        ).order_by('-follower_count')[:10]  # Limit to top 10 users

        results = [
            {
                "id": user.id,
                "username": user.user.username,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
                "follower_count": user.follower_count
            }
            for user in users
        ]

        return Response(results)


class PopularPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user.userprofile

        followed_users = user.following.values_list('to_user', flat=True)

        posts = Post.objects.filter(
            user__in=followed_users
        ).annotate(
            like_count=Count('likes')
        ).order_by('-created_at', '-like_count')[:20]


        results = [
            {
                "id": post.id,
                "user": post.user.user.username,
                "content": post.content,
                "created_at": post.created_at,
                "like_count": post.like_count
            }
            for post in posts
        ]

        return Response(results)












