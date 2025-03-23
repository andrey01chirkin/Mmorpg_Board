from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
import random


CATEGORY_CHOICES = [
    ('tank', 'Танки'),
    ('healer', 'Хилы'),
    ('dd', 'ДД'),
    ('trader', 'Торговцы'),
    ('guildmaster', 'Гилдмастеры'),
    ('questgiver', 'Квестгиверы'),
    ('blacksmith', 'Кузнецы'),
    ('leatherworker', 'Кожевники'),
    ('alchemist', 'Зельевары'),
    ('spellmaster', 'Мастера заклинаний'),
]

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отклик от {self.author} на {self.post}'


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = ''.join(random.choices('0123456789', k=6))
        self.save()