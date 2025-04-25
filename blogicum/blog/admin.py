from django.contrib import admin
from .models import Post, Category, Location

admin.site.site_title = "Администрирование Блогикума"
admin.site.site_header = "Блог"
admin.site.index_title = "Управление контентом"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "pub_date", "is_published")
    list_filter = ("category", "is_published", "pub_date")
    search_fields = ("title", "text")
    empty_value_display = "---"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published")
    search_fields = ("title",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published")
