from django.contrib import admin
from .models import Post, Response

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted',)
