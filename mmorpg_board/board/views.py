from django.shortcuts import render, redirect
from .forms import CustomRegistrationForm
from .models import EmailConfirmation
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import EmailCodeForm
from django.contrib.auth import login

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
                login(request, user)
                return redirect('/')
            else:
                form.add_error('code', 'Неверный код')
    else:
        form = EmailCodeForm()
    return render(request, 'board/confirm_email.html', {'form': form})

