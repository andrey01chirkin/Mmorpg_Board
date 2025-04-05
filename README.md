# Доска объявлений MMORPG на Django

## Установка
1. Клонирование репозитория\
``` git clone https://github.com/andrey01chirkin/Mmorpg_Board.git ```
2. Открыть проект в Pycharm
3. Создание виртуального окружения\
``` python -m venv venv ```
4. Активация виртуального окружения\
``` venv/Scripts/activate ```
5. Установка зависимостей\
``` pip install -r requirements.txt ```
6. На одном уровне с папкой venv создать файл .env, где создать переменные email, email_password, SECRET_KEY
- email - дефолтная почта с которой будут отправляться письма
- email_password - пароль для отправки писем
- SECRET_KEY можно сгенерировать в консоле python: import secrets; cprint(secrets.token_urlsafe(50))
7. Перейти в проект: cd mmorpg_board
8. Запустить сервер: python manage.py runserver
9. Для запуска планировщика в другой терминале выполнить команду: python manage.py start_scheduler