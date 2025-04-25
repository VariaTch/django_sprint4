from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from blog.models import Post, Category


def index(request):
    posts = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by("-pub_date")[:5]

    return render(
        request,
        "blog/index.html",
        {
            "title": "Главная страница",
            "posts": posts,
        },
    )


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related("category"),
        pk=id,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    return render(
        request,
        "blog/detail.html",
        {
            "title": post.title,
            "post": post,
        },
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by("-pub_date")

    return render(
        request,
        "blog/category.html",
        {
            "title": category.title,
            "category": category,
            "posts": posts,
        },
    )
