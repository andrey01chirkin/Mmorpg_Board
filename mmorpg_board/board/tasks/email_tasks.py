from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from board.models import Subscription, Post
import logging

logger = logging.getLogger(__name__)

def send_weekly_updates():
    """Отправка еженедельных обновлений по категориям"""
    logger.info("Запуск задачи еженедельной рассылки новостей")
    today = now().date()
    last_week = today - timedelta(days=7)

    try:
        subscriptions = Subscription.objects.select_related('user', 'category')

        # Словарь для группировки постов по пользователям
        user_posts = {}

        for sub in subscriptions:
            start_of_week = now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
            end_of_week = now().replace(hour=23, minute=59, second=59, microsecond=999999)

            # Получаем новые посты за последнюю неделю в подписанных категориях
            new_posts = Post.objects.filter(
                category=sub.category,
                created_at__range=[start_of_week, end_of_week]
            )

            if new_posts.exists():
                if sub.user not in user_posts:
                    user_posts[sub.user] = {}

                # Группировка по категориям
                if sub.category.name not in user_posts[sub.user]:
                    user_posts[sub.user][sub.category.name] = []

                # Добавляем посты в список пользователя по категориям
                user_posts[sub.user][sub.category.name].extend(
                    [f'<li><a href="http://127.0.0.1:8000/post/{post.id}/">{post.title}</a></li>' for post in new_posts]
                )

        # Отправляем одно письмо для каждого пользователя с форматированным HTML содержимым
        for user, categories in user_posts.items():
            if categories:
                message = f"Здравствуйте, {user.username}!<br><br>Вот новые объявления в ваших категориях за последнюю неделю:<br><br>"

                for category, posts in categories.items():
                    message += f"<strong>{category}:</strong><ul>{''.join(posts)}</ul>"

                try:
                    send_mail(
                        subject="Еженедельная рассылка новых объявлений",
                        message="",
                        html_message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    logger.info(f"Письмо успешно отправлено пользователю {user.username} на адрес {user.email}")
                except Exception as e:
                    logger.error(f"Ошибка при отправке письма пользователю {user.username}: {e}")
            else:
                logger.info(f"Нет новых объявлений для пользователя {user.username}")

    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {e}")
