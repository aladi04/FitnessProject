from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q


class Post(models.Model):

    CATEGORY_CHOICES = [
        ("workout", "Workout"),
        ("nutrition", "Nutrition"),
        ("motivation", "Motivation"),
        ("general", "General Discussion"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    # NEW FIELD → category with restriction
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="general")

    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   # ✅ new timestamp field

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def like(self, user):
        """Like or unlike a post."""
        like, created = Like.objects.get_or_create(post=self, user=user)
        if not created:
            like.delete()
        return created

    def add_comment(self, user, comment_text):
        """Add a comment to the post."""
        return Comment.objects.create(post=self, author=user, content=comment_text)

    @classmethod
    def search(cls, query):
        """Search posts by title, content, or category."""
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__icontains=query)
        )

    @classmethod
    def sort_by(cls, queryset, field):
        """Sort queryset by given field, with validation."""
        allowed_fields = ["title", "created_at", "-created_at", "category"]
        if field not in allowed_fields:
            field = "-created_at"  # fallback to newest first
        return queryset.order_by(field)
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("post", "user")  # prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="actions")
    verb = models.CharField(max_length=255)  # e.g., "liked your post", "commented on your post"
    target_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor.username} {self.verb} {self.target_post}"