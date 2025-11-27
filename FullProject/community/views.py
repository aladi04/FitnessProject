from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment

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
    post.like(request.user)
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

    return redirect("post_details", post_id=post.id)
