from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.http import Http404
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm, ProfileEditForm
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models import Count

POSTS_PER_PAGE = 10
User = get_user_model()


def index(request):
    """Главная страница: вывод постов с пагинацией и числом комментариев."""
    post_list = (
        Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/index.html",
        {
            "title": "Главная страница",
            "posts": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


def post_detail(request, id):
    """Детальная страница поста."""
    post = get_object_or_404(Post.objects.select_related("category"), pk=id)

    if post.author != request.user:
        if (
            not post.is_published
            or post.pub_date > timezone.now()
            or not post.category.is_published
        ):
            raise Http404

    form = CommentForm()
    comments = post.comments.all()

    return render(
        request,
        "blog/detail.html",
        {
            "title": post.title,
            "post": post,
            "form": form,
            "comments": comments,
        },
    )


def category_posts(request, category_slug):
    """Страница категории: посты этой категории с пагинацией."""
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)

    post_list = (
        Post.objects.filter(
            category=category, is_published=True, pub_date__lte=timezone.now()
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/category.html",
        {
            "title": category.title,
            "category": category,
            "posts": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


@login_required
def post_create(request):
    """Создание нового поста."""
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()

    return render(request, "blog/create.html", {"form": form})


@login_required(login_url="/auth/login/")
def post_edit(request, id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=id)

    if post.author != request.user:
        return redirect("blog:post_detail", id=post.id)

    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/create.html", {"form": form, "post": post})


@login_required(login_url="/auth/login/")
def post_delete(request, post_id):
    """Подтверждение и удаление поста."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", id=post.id)

    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)

    form = PostForm(instance=post)
    return render(request, "blog/create.html", {"form": form, "post": post})


def profile(request, username):
    """Страница профиля пользователя."""
    user = get_object_or_404(User, username=username)

    qs = Post.objects.filter(author=user)
    if request.user.username != username:
        qs = qs.filter(is_published=True, pub_date__lte=timezone.now())
    posts = qs.annotate(comment_count=Count("comments")).order_by("-pub_date")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/profile.html",
        {
            "profile": user,
            "posts": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


class CommentMixin(LoginRequiredMixin):
    """Set default model and template for comment views."""

    model = Comment
    template_name = "blog/comment.html"


class CommentCreateView(CommentMixin, CreateView):
    """Создание комментария."""

    form_class = CommentForm
    _post = None

    def dispatch(self, request, *args, **kwargs):
        """Получение поста или ошибка 404."""
        self._post = get_object_or_404(
            Post,
            pk=kwargs["post_id"],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Сохранение нового комментария."""
        form.instance.author = self.request.user
        form.instance.post = self._post
        return super().form_valid(form)

    def get_success_url(self):
        """Переход на страницу поста."""
        return reverse_lazy("blog:post_detail", kwargs={"id": self._post.pk})


class CommentUpdDelMixin(CommentMixin, View):
    """Mixin для изменения и удаления комментариев."""

    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        """Проверка авторства комментария."""
        comment = get_object_or_404(Comment, pk=kwargs["comment_id"])
        if comment.author != request.user:
            return redirect("blog:post_detail", id=self.kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Переход на страницу поста."""
        return reverse_lazy("blog:post_detail",
                            kwargs={"id": self.kwargs["post_id"]})


class CommentUpdateView(CommentUpdDelMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentUpdDelMixin, DeleteView):
    """Удаление комментария."""

    pass


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    template_name = "blog/user.html"
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        """Возвращает объект пользователя."""
        return self.request.user

    def get_success_url(self):
        """Редирект на профиль пользователя."""
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class AboutPageView(TemplateView):
    """Статичная страница 'О проекте'."""

    template_name = "pages/about.html"


class RulesPageView(TemplateView):
    """Статичная страница 'Правила сайта'."""

    template_name = "pages/rules.html"


def send_test_email(request):
    send_mail(
        "Тема письма",
        "Текст письма.",
        "from@example.com",
        ["to@example.com"],
        fail_silently=False,
    )
    return HttpResponse("Письмо отправлено (сохранено в файл).")
