from django.contrib import admin
from .models import *

from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'type', 'status')  # فیلدهایی که می‌خواهید نمایش داده شوند
    search_fields = ('user__username', 'type')


    @admin.display(description='Status')
    def get_status(self, obj):
        return 'Active' if obj.status else 'Inactive'
# admin.site.register(UserProfile)

@admin.register(Connection)
class ConectionAdmin(admin.ModelAdmin):
    list_display = ('id','from_user','to_user')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'title', 'content', 'created_at')

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    tag_list.short_description = 'Tags'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'post','content','parent','created_at')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id','user','post', 'created_at')

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
   list_display = ('id','name','created_at')

