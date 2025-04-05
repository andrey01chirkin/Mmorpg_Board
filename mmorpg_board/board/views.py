import os

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from dotenv import load_dotenv

from .forms import CustomRegistrationForm, ReplyForm, SubscriptionForm
from .models import EmailConfirmation, Post, Reply, Category, Subscription
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import EmailCodeForm
from django.contrib.auth import login, logout
from .forms import EmailLoginForm
from django.contrib.auth.decorators import login_required
from .forms import PostForm


def home_view(request):
    posts = Post.objects.all().order_by('-created_at')  # Сортировка по дате создания (новые сверху)
    return render(request, 'board/home.html', {'posts': posts})

def register_view(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            confirmation = EmailConfirmation.objects.create(user=user)
            confirmation.generate_code()

            load_dotenv()

            # Отправка письма
            send_mail(
                subject='Ваш код подтверждения',
                message=f'Код подтверждения: {confirmation.code}',
                from_email=os.getenv('email'),
                recipient_list=[user.email],
            )
            request.session['user_id'] = user.id
            return redirect('confirm_email')
    else:
        form = CustomRegistrationForm()
    return render(request, 'board/register.html', {'form': form})


def confirm_email_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = User.objects.get(id=user_id)
    confirmation = EmailConfirmation.objects.get(user=user)

    if request.method == 'POST':
        form = EmailCodeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['code'] == confirmation.code:
                user.is_active = True
                user.save()
                confirmation.delete()
                return redirect('registration_success')
            else:
                form.add_error('code', 'Неверный код')
    else:
        form = EmailCodeForm()

    return render(request, 'board/confirm_email.html', {'form': form})


def registration_success_view(request):
    return render(request, 'board/registration_success.html')


def login_view(request):
    form = EmailLoginForm()
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('/')
    return render(request, 'board/login.html', {'form': form})

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Добавили request.FILES
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('/')
    else:
        form = PostForm()
    return render(request, 'board/create_post.html', {'form': form})


def post_detail_view(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        accepted_replies = post.replies.filter(accepted=True)

        if request.method == 'POST':

            if request.user == post.author:
                messages.error(request, "Вы не можете оставить отклик на свое собственное объявление.")
                return redirect('post_detail', post_id=post_id)

            form = ReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.author = request.user
                reply.post = post
                reply.save()

                # Отправка уведомления автору объявления
                send_mail(
                    subject='Новый отклик на ваше объявление',
                    message=f'На ваше объявление "{post.title}" поступил отклик от {request.user.username}: {reply.content}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[post.author.email],
                    fail_silently=False,
                )

                messages.success(request, "Ваш отклик успешно отправлен!")
                return redirect('post_detail', post_id=post_id)

        else:
            form = ReplyForm()

        return render(request, 'board/post_detail.html', {
            'post': post,
            'form': form,
            'replies': accepted_replies,
        })

    except Exception as e:
        print(f"Ошибка: {e}")
        return render(request, 'board/error.html', {'message': str(e)})



def my_posts_view(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'board/my_posts.html', {'posts': posts})


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return redirect('my_posts')


def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)
    return render(request, 'board/edit_post.html', {'form': form, 'post': post})


@login_required
def my_replies_view(request):
    user_posts = Post.objects.filter(author=request.user)
    replies = Reply.objects.filter(post__author=request.user)

    # Получаем параметры фильтрации
    category = request.GET.get('category')
    status = request.GET.get('status')  # Новый параметр статуса

    # Фильтрация по категории
    if category:
        replies = replies.filter(post__category__name=category)

    # Фильтрация по статусу принятия
    if status == 'accepted':
        replies = replies.filter(accepted=True)
    elif status == 'not_accepted':
        replies = replies.filter(accepted=False)

    # Получаем категории только тех объявлений, которые имеют отклики
    categories = Category.objects.filter(
        Q(post__in=user_posts) & Q(post__replies__isnull=False)
    ).distinct()

    return render(request, 'board/my_replies.html', {
        'replies': replies,
        'categories': categories,
        'user_posts': user_posts,
    })




@login_required
def accept_reply_view(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id, post__author=request.user)
    reply.accepted = True
    reply.save()

    # Отправка уведомления пользователю
    send_mail(
        'Ваш отклик принят',
        f'Ваш отклик на объявление "{reply.post.title}" был принят!',
        settings.DEFAULT_FROM_EMAIL,
        [reply.author.email],
        fail_silently=False,
    )

    return redirect('my_replies')

@login_required
def delete_reply_view(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id, post__author=request.user)
    reply.delete()
    return redirect('my_replies')


@login_required
def subscriptions(request):
    user_subscriptions = Subscription.objects.filter(user=request.user)
    categories = Category.objects.exclude(id__in=user_subscriptions.values_list('category_id', flat=True))

    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            return redirect('subscriptions')
    else:
        form = SubscriptionForm()

    return render(request, 'board/subscriptions.html', {
        'form': form,
        'subscriptions': user_subscriptions,
        'categories': categories
    })

@login_required
def unsubscribe(request, sub_id):
    subscription = Subscription.objects.get(id=sub_id, user=request.user)
    if subscription:
        subscription.delete()
    return redirect('subscriptions')