from django.contrib import admin
from .models import Post, Comment, Category, LinkCategory

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(LinkCategory)