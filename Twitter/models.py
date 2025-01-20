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
        upload_to='profile_pics/', blank=True,default='media/profile_pics/nody-عکس-پروفایل-مخصوص-واتساپ-؛-؛-1717325475.jpg')


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
        unique_together = ('post', 'user')


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ViewPost(models.Model):
    from_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='view_posts')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'post')  # هر کاربر تنها یک بار می‌تواند یک پست را مشاهده کند


class Post(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=250)
    hashtags = models.ManyToManyField('Hashtag', related_name="posts", default=None)
    post_picture = models.ImageField(upload_to='post_pics/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def can_view(self, viewer):
        """
        بررسی می‌کند آیا کاربر می‌تواند این پست را ببیند یا خیر.
        """
        if self.user.type == False:  # حساب عمومی
            return True
        elif self.user.followers.filter(id=viewer.id).exists():  # اگر کاربر فالوور باشد
            return True
        return False

    @property
    def views_count(self):
        return self.views.count()
    @property
    def likes_count(self):

        return self.likes.count()

    @property
    def comments_count(self):

        return self.comments.count()

    @property
    def nested_comments(self):
        # کامنت‌های تو در تو
        return self.comments.filter(parent=None)


class FollowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    from_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='sent_follow_requests')
    to_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='received_follow_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_follow_request')
        ]


class Notification(models.Model):
    STATUS_CHOICES = [
        ('follow_request', 'Follow Request'),
        ('comment_to_post', 'Comment to Post'),
        ('reply_to_comment', 'Reply to Comment'),
        ('likes_for_post', 'Likes for Post'),
    ]
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='notifications_actor')
    target = models.CharField(max_length=255, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_read = models.BooleanField(default=False)
    message = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        ordering = ['-created_at']  # مرتب‌سازی پیش‌فرض

    def __str__(self):
        return f"Notification ({self.status}) for {self.user}"



