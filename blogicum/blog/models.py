from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; "
        "разрешены символы латиницы, цифры, дефис "
        "и подчёркивание.",
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField("Название места", max_length=256)
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть местоположение.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату "
        "и время в будущем — можно делать "
        "отложенные публикации.",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name="Категория",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="post_images/",
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    post = models.ForeignKey(
        Post,
        verbose_name="Публикация",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User, verbose_name="Автор комментария", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(verbose_name="Добавлено",
                                      auto_now_add=True)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий к публикации {self.post.title} от {self.author}."
