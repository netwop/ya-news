from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.forms import CommentForm


HOME_URL = reverse('news:home')


def news_detail_url(pk):
    return reverse('news:detail', args=(pk,))


def test_news_count(news, author_client):
    response = author_client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

def test_news_order(news, author_client):
    response = author_client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [obj.date for obj in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates

def test_comments_order(news_author_comments, author_client):
    news, _, _ = news_author_comments
    response = author_client.get(news_detail_url(news.id))
    news_from_response = response.context['news']
    all_comments = news_from_response.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps

def test_anonymous_client_has_no_form(news_author_comments, client):
    news, _, _ = news_author_comments
    response = client.get(news_detail_url(news.id))
    assert 'form' not in response.context

def test_authorized_client_has_form(news_author_comments, author_client):
    news, _, _ = news_author_comments
    response = author_client.get(news_detail_url(news.id))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
