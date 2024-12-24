# apps.py
from django.apps import AppConfig

class TwitterConfig(AppConfig):  # نام کلاس باید مطابق با اپلیکیشن باشد
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Twitter'  # نام اپلیکیشن

    def ready(self):
        import Twitter.signals  # فایل سیگنال‌ها را وارد کنید

