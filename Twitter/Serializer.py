from rest_framework import serializers
from .models import UserProfile, Connection,Post,Like,Comment,Hashtag
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # نمایش اطلاعات جزئی‌تر از User

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'last_name', 'first_name', 'bio', 'type', 'status', 'profile_picture']
        read_only_fields = ['id', 'user']  # مشخص کردن فیلدهای فقط خواندنی

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id', 'from_user', 'to_user']
        read_only_fields = ['id', 'from_user']  # از تغییر `from_user` جلوگیری می‌کنیم

    def validate(self, data):
        """ولیدیشن برای جلوگیری از دنبال کردن خود"""
        if data['from_user'] == data['to_user']:
            raise serializers.ValidationError("شما نمی توانید خودتون رو فالو کنید!!.")
        return data

class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'parent', 'created_at', 'replies']
        read_only_fields = ['id', 'user', 'created_at', 'replies']

    def get_replies(self, obj):
        # دریافت تمام پاسخ‌های یک کامنت
        if obj.children.exists():
            return CommentSerializer(obj.children.all(), many=True).data
        return []

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']

class CradPostSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)  # مشخصات سازنده پست
    likes_count = serializers.IntegerField( read_only=True)  # تعداد لایک‌ها
    comments_count = serializers.IntegerField( read_only=True)  # تعداد کامنت‌ها
    nested_comments = CommentSerializer(many=True, read_only=True)  # کامنت‌های پست
    hashtags = HashtagSerializer(many=True)  # اضافه کردن هشتگ‌ها به پست
    views_count = serializers.IntegerField( read_only=True)
    class Meta:
        model = Post
        fields = [
            'id', 'post_picture', 'title', 'content', 'hashtags', 'created_at',
            'user', 'likes_count', 'comments_count', 'nested_comments', 'views_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'likes_count', 'comments_count']

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content','post_picture']
        read_only_fields=['id']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserLoginDTO(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=20,min_length=8,write_only=True)
    refresh = serializers.CharField(required=False)

class UserRejisterDTO(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=20,min_length=8,write_only=True)
    email = serializers.EmailField(max_length=100)
    first_name = serializers.CharField(max_length=50,required=False)
    last_name = serializers.CharField(max_length=50,required=False)
    refresh = serializers.CharField(required=False)

class LogoutDTO(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

class UserProfileDTO(serializers.Serializer):
    first_name = serializers.CharField(max_length=50,required=False)
    last_name = serializers.CharField(max_length=50,required=False)
    bio = serializers.CharField(max_length=200,required=False)
    type = serializers.BooleanField(required=False)
    profile_picture = serializers.ImageField(required=False)

class PostDTO(serializers.Serializer):
    title = serializers.CharField(required=True,max_length=50)
    content = serializers.CharField(required=True,max_length=250)
    post_picture = serializers.ImageField(required=False)

class EditPostDTO(serializers.Serializer):
    content = serializers.CharField(required=True,max_length=250)

class PostCommentsDTO(serializers.Serializer):
    content = serializers.CharField(required=True,max_length=250)
    parent_id = serializers.IntegerField(required=False)






