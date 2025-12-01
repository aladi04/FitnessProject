from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Notification

@login_required
def notifications_list(request):
    """
    Show user's notifications
    """
    notifications = request.user.notifications.all()
    # Mark all as read when viewing the list (optional, or do per-item)
    # notifications.update(is_read=True) 
    return render(request, "community/notifications.html", {
        "notifications": notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to the target post if it exists
    if notification.target_post:
        return redirect("post_details", post_id=notification.target_post.id)
    return redirect("notifications_list")

@login_required
def community_home(request):
    """
    Home page showing list of posts with working search + sort.
    """
    query = request.GET.get("q") or ""
    sort_field = request.GET.get("sort") or "-created_at"

    # start with all posts
    posts = Post.objects.all()

    # if there’s a search, filter by it
    if query:
        posts = Post.search(query)

    # apply sorting to the resulting queryset
    posts = Post.sort_by(posts, sort_field)

    context = {
        "posts": posts,
        "current_sort": sort_field,
        "current_query": query,
    }
    return render(request, "community/index.html", context)



@login_required
def create_post(request):
    """
    Create a post using POST data + image.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        category = request.POST.get("category")
        image = request.FILES.get("image")

        post = Post.objects.create(
            author=request.user,
            title=title,
            content=content,
            category=category,
            image=image,
        )

        messages.success(request, "✅ Post created successfully!")
        return redirect("post_details", post_id=post.id)

    return render(request, "community/create_post.html", {
        "categories": Post.CATEGORY_CHOICES
    })

@login_required
def post_details(request, post_id):
    """
    Shows post details + comments + like count.
    """
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    return render(request, "community/post_details.html", {
        "post": post,
        "comments": comments,
    })

@login_required
def update_post(request, post_id):
    """
    Update a post (only by its author).
    """
    post = get_object_or_404(Post, id=post_id)

    # only the author can edit
    if post.author != request.user:
        messages.error(request, "❌ You’re not allowed to edit this post.")
        return redirect("post_details", post_id=post.id)

    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.category = request.POST.get("category")

        if "image" in request.FILES:
            post.image = request.FILES["image"]

        post.save()
        messages.success(request, "✅ Post updated successfully!")
        return redirect("post_details", post_id=post.id)

    return render(request, "community/update_post.html", {
        "post": post,
        "categories": Post.CATEGORY_CHOICES,
    })

@login_required
def delete_post(request, post_id):
    """
    Delete a post (only by its author).
    """
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "❌ You’re not allowed to delete this post.")
        return rediresct("post_details", post_id=post.id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "🗑️ Post deleted successfully!")
        return redirect("community")

    return render(request, "community/confirm_delete.html", {"post": post})


@login_required
def like_post(request, post_id):
    """
    Calls post.like(user)
    """
    post = get_object_or_404(Post, id=post_id)
    liked = post.like(request.user)

    # Create notification if liked (not unliked) and user is not author
    if liked and request.user != post.author:
        Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb="liked your post",
            target_post=post
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })

    return redirect("post_details", post_id=post.id)
    

@login_required
def add_comment(request, post_id):
    """
    Calls post.add_comment(user, text)
    """
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        comment = request.POST.get("content")
        post.add_comment(request.user, comment)

        # Create notification
        if request.user != post.author:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb="commented on your post",
                target_post=post
            )

    return redirect("post_details", post_id=post.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Users can only delete their own comments
    if comment.author != request.user:
        messages.error(request, "You can only delete your own comments.")
        return redirect("post_details", post_id=comment.post.id)

    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect("post_details", post_id=post_id)

@login_required
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        messages.error(request, "You can only edit your own comments.")
        return redirect("post_details", post_id=comment.post.id)

    if request.method == "POST":
        new_content = request.POST.get("content")
        if new_content:
            comment.content = new_content
            comment.save()
            messages.success(request, "Comment updated successfully.")
            return redirect("post_details", post_id=comment.post.id)

    # Render a simple edit template or handle inline editing via JS? 
    # For now let's create a dedicated template for editing comments
    return render(request, "community/update_comment.html", {"comment": comment})
