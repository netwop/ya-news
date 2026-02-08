import pytest

# Импортируем класс клиента.
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment

from datetime import datetime, timedelta

User = get_user_model()

@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(author):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news

@pytest.fixture
def one_news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date = datetime.today()
    )
    return news

@pytest.fixture
def comment(one_news, author):
    comment = Comment.objects.create(
            news=one_news, author=author, text=f'Tекст',
        )
    return comment

@pytest.fixture
def one_news_id(one_news):
    return (one_news.id,)

@pytest.fixture
def comment_id(comment, author):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def bad_words_data():
    return {
        'text': 'Плохой текст',
    }


@pytest.fixture
def news_author_comments(author):
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    author = User.objects.create(username='Комментатор')
    # Запоминаем текущее время:
    now = timezone.now()
    # Создаём комментарии в цикле.
    comments = []
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
        comments.append(comment)
    return news, author, comments