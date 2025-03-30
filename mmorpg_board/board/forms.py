from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Post, Reply
import re


class CustomRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Имя пользователя',
        error_messages={'required': 'Это поле обязательно'}
    )

    email = forms.EmailField(
        label='Email',
        error_messages={'required': 'Это поле обязательно', 'invalid': 'Введите корректный email'}
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        error_messages={'required': 'Это поле обязательно'}
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        error_messages={'required': 'Это поле обязательно'}
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Проверка длины
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
        # Цифра
        if not re.search(r'\d', password):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну цифру')
        # Заглавная буква
        if not re.search(r'[A-ZА-Я]', password):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        # Строчная буква
        if not re.search(r'[a-zа-я]', password):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну строчную букву')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError('Пароли не совпадают')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False
        if commit:
            user.save()
        return user


class EmailCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label='Введите код из e-mail',
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('Неверный email или пароль')

            if not user.is_active:
                raise forms.ValidationError('Пожалуйста, подтвердите ваш e-mail перед входом')

            user = authenticate(username=user.username, password=password)
            if user is None:
                raise forms.ValidationError('Неверный email или пароль')

            cleaned_data['user'] = user

        return cleaned_data


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']
        labels = {
            'title': 'Заголовок',
            'category': 'Категория',
            'content': 'Содержание',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': CKEditorUploadingWidget(attrs={'class': 'form-control'}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        labels = {'content': 'Текст отклика'}
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите ваш отклик...'}),
        }