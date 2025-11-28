from django.contrib import admin
from .models import Post, Comment, Like, Notification

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at', 'like_count', 'comment_count')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'category')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    # Display related counts
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = "Likes"

    def comment_count(self, obj):
        return obj.comment_count
    comment_count.short_description = "Comments"

    def has_change_permission(self, request, obj=None):
        # Users can only edit their own posts
        if obj is not None and obj.author != request.user:
            return False
        return super().has_change_permission(request, obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'author__username', 'content')
    ordering = ('-created_at',)

    def has_change_permission(self, request, obj=None):
        # Users can only edit their own comments
        if obj is not None and obj.author != request.user:
            return False
        return super().has_change_permission(request, obj)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')
    search_fields = ('post__title', 'user__username')

    def has_change_permission(self, request, obj=None):
        # Users can only edit their own likes
        if obj is not None and obj.user != request.user:
            return False
        return super().has_change_permission(request, obj)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'target_post', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'actor__username', 'verb')
    ordering = ('-created_at',)
