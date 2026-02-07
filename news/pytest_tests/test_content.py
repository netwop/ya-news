# test_content.py
import pytest
from pytest_lazy_fixtures import lf

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from datetime import datetime, timedelta

from news.models import Comment, News
from news.forms import CommentForm


HOME_URL = reverse('news:home')


def test_news_count(news, author_client):
    # Загружаем главную страницу.
    response = author_client.get(HOME_URL)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

def test_news_order(news, author_client):
    response = author_client.get(HOME_URL)
    object_list = response.context['object_list']
    assert len(object_list) > 0
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates

def test_comments_order(news_author_comments, author_client):
    news, author, comments = news_author_comments
    response = author_client.get(reverse ('news:detail', args=(news.id,)))
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    # Получаем объект новости.
    news_from_response = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news_from_response.comment_set.all()
    # Собираем временные метки всех комментариев.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps

def test_anonymous_client_has_no_form(news_author_comments, client):
    news, author, comments = news_author_comments
    response = client.get(reverse ('news:detail', args=(news.id,)))
    assert 'form' not in response.context

def test_authorized_client_has_form(news_author_comments, author_client):
    news, author, comments = news_author_comments
    response = author_client.get(reverse ('news:detail', args=(news.id,)))
    assert 'form' in response.context
    # Проверим, что объект формы соответствует нужному классу формы.
    assert isinstance (response.context['form'], CommentForm)