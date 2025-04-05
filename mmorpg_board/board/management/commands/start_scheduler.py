from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from board.tasks.email_tasks import send_daily_updates
import logging

logger = logging.getLogger(__name__)

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Удаляем старые задачи из базы данных."""
    try:
        DjangoJobExecution.objects.delete_old_job_executions(max_age)
        logger.info("Старые задачи успешно удалены.")
    except Exception as e:
        logger.error(f"Ошибка при удалении старых задач: {e}")

class Command(BaseCommand):
    help = "Запуск планировщика задач"

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone="Europe/Moscow")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        try:
            # Задача рассылки новостей каждую неделю в понедельник в 9:00
            scheduler.add_job(
                send_daily_updates,
                trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),  # Каждый понедельник в 9:00
                id="weekly_newsletter",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Задача рассылки новостей добавлена.")
            self.stdout.write(self.style.SUCCESS("Задача рассылки новостей добавлена."))

            # Задача очистки старых заданий (еженедельно в понедельник в 00:00)
            scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),  # Каждый понедельник в 00:00
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )
            logger.info("Задача очистки старых заданий добавлена.")
            self.stdout.write(self.style.SUCCESS("Задача очистки старых заданий добавлена."))

            # Запуск планировщика в блокирующем режиме
            logger.info("Планировщик успешно запущен.")
            scheduler.start()
        except Exception as e:
            logger.error(f"Ошибка при запуске планировщика: {e}")
            self.stdout.write(self.style.ERROR(f"Ошибка при запуске планировщика: {e}"))
