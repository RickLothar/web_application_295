from django.contrib import admin
from .models import Result, Video, Channel, VideoOnline, ViewCount


# Register your models here.
admin.site.register(Result)
admin.site.register(Video)
admin.site.register(Channel)
admin.site.register(VideoOnline)
admin.site.register(ViewCount)
