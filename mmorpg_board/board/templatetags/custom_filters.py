from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def truncate_chars(value, num):
    """Обрезает текст до заданного количества символов с многоточием, удаляя HTML-теги."""
    # Убираем все HTML-теги из текста
    plain_text = strip_tags(value)
    # Обрезаем текст до указанного количества символов
    if len(plain_text) > num:
        return plain_text[:num] + '...'
    return plain_text
