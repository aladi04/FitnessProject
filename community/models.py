from django.db import models
from accounts.models import Member
from django.core.validators import MinLengthValidator, FileExtensionValidator, ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


# Create your models here.
 

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('workout', 'Workout'),
        ('nutrition', 'Nutrition'),
        ('motivation', 'Motivation'),
        ('progress', 'Progress'),
        ('other', 'Other'),
    ]
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)]
    )
    content = models.TextField(
        validators=[MinLengthValidator(10)]
    )
    author = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    likes = models.IntegerField(default=0)
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    

    def __str__(self):
        return self.title
    
    def like(self):
        self.likes += 1
        self.save()

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__icontains=query)
        )

    @classmethod
    def sort_by(cls, field):
        if field in ['title', 'created_at', 'likes', 'category']:
            return cls.objects.order_by(field)
        return cls.objects.all()
    

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(validators=[MinLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    class Meta:
        ordering = ['-created_at']