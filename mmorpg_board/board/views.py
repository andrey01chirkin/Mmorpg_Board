from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomRegistrationForm
from .models import EmailConfirmation, Post
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import EmailCodeForm
from django.contrib.auth import login
from .forms import EmailLoginForm
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from ckeditor_uploader.views import upload


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

            # Отправка письма
            send_mail(
                subject='Ваш код подтверждения',
                message=f'Код подтверждения: {confirmation.code}',
                from_email='chirkin.andrey377@gmail.com',
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


def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'board/post_detail.html', {'post': post})


def my_posts_view(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'board/my_posts.html', {'posts': posts})


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
