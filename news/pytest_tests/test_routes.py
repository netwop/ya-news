import pytest
from pytest_django.asserts import assertRedirects

from pytest_lazy_fixtures import lf
from http import HTTPStatus

from django.urls import reverse

from news.models import News, Comment


@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('users:login', None),
        ('users:signup', None),
        ('news:detail', lf('one_news_id'))
    ],
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_availability_for_anonymous_user(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ],
)
@pytest.mark.parametrize(
   'name, args',
    [
      ('news:edit', lf('comment_id')),
      ('news:delete', lf('comment_id')),
    ],
)
def test_pages_availability_for_different_users(
    parametrized_client, name, args, expected_status
    ):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    [
        ('news:edit', lf('comment_id')),
        ('news:delete', lf('comment_id')),
    ],
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)