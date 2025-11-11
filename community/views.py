from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment


def community_home(request):
    """
    Home page showing list of posts.
    Includes search + sorting.
    """
    query = request.GET.get("q")       # search query
    sort_field = request.GET.get("sort", "-created_at")  # default: newest first

    # use class diagram search method
    if query:
        posts = Post.search(query)
    else:
        posts = Post.sort_by(sort_field)

    return render(request, "community/index.html", {
        "posts": posts,
        "current_sort": sort_field,
    })


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
