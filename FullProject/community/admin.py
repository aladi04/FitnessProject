from django.contrib import admin
from .models import Post, Comment, Like
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at', 'like_count', 'comment_count')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'authorusername', 'category')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    # Display related counts
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = "Likes"

    def comment_count(self, obj):
        return obj.comment_count
    comment_count.short_description = "Comments"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('posttitle', 'authorusername', 'content')
    ordering = ('-created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')
    search_fields = ('posttitle', 'user__username')