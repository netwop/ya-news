from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
import pytest

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
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
def one_news_id_for_args(one_news):
    return (one_news.id,)


@pytest.fixture
def comment_id_for_args(comment, author):
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
def one_news_with_author_comments(author):
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now - timedelta(days=index)
        comment.save()
        comments.append(comment)
    return news
