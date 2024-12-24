from django.contrib.auth.models import User
from django.db import models




class UserProfile(models.Model):
    TYPE_CHOICES = (
        (True,'خصوصی'),
        (False,'عمومی')
    )
    STATUS_CHOICES = (
        (True,'فعال'),
        (False,'غیرفعال')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # last_seen = models.DateTimeField(auto_now_add=True)
    last_name = models.CharField(max_length=120,blank=True,default='')
    first_name = models.CharField(max_length=120,blank=True,default='')
    bio = models.TextField(blank=True,default='من از توییتر فارسی استفاده میکنم!')
    type = models.BooleanField(choices=TYPE_CHOICES,default=False)
    status = models.BooleanField( choices=STATUS_CHOICES,default=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True,default='profile_pics/nody-عکس-پروفایل-مخصوص-واتساپ-؛-؛-1717325475.jpg')


    def __str__(self):
        return self.user.username


class Connection(models.Model):
    from_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='followers')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_following')
        ]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"


class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # جلوگیری از لایک‌های تکراری توسط یک کاربر


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # نام هشتگ
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=50)  # افزایش محدودیت طول عنوان برای انعطاف بیشتر
    content = models.TextField(max_length=250)  # حذف محدودیت طول برای محتوای متن
    hashtags = models.ManyToManyField(Hashtag, related_name="posts",default=None)  # ارتباط چند به چند با هشتگ‌ها
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        # بهبود برای خوانایی و عملکرد
        return self.likes.count()

    @property
    def comments_count(self):
        # بهبود برای خوانایی و عملکرد
        return self.comments.count()

    @property
    def nested_comments(self):
        # کامنت‌های تو در تو
        return self.comments.filter(parent=None)






