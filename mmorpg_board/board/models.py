import random
from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField


# Модель категорий
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Модель подписок на категории
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} -> {self.category.name}"


# Модель объявлений
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()  # Используем CKEditor с загрузкой
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/post/{self.id}/"


# Модель откликов на объявления
class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Текст отклика")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False, verbose_name="Принят")

    def __str__(self):
        return f"Отклик от {self.author} на {self.post}"


# Модель для подтверждения e-mail
class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = ''.join(random.choices('0123456789', k=6))
        self.save()
