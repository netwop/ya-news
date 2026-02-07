# test_logic.py
from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
import pytest
from http import HTTPStatus

# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_comment(author_client, author, form_data):
    url = reverse('news:detail', kwargs={'pk': News.object.pk}) + '#comments'
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, что был выполнен редирект на страницу успешного добавления заметки:
    assertRedirects(response, reverse('news:detail', kwargs={'pk': News.object.pk}) + '#comments')
    # Считаем общее количество заметок в БД, ожидаем 1 заметку.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.title == form_data['title']
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    # Вроде бы здесь нарушен принцип "один тест - одна проверка";
    # но если хоть одна из этих проверок провалится -
    # весь тест можно признать провалившимся, а последующие невыполненные проверки
    # не внесли бы в отчёт о тесте ничего принципиально важного.

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    url = reverse('news:detail')
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, new):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=(News.comment.id,))
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    assertRedirects(response, reverse('news:edit', args=(News.comment.id,)))
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    new.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert new.title == form_data['title']
    assert new.text == form_data['text']


def test_other_user_cant_edit_comment(not_author_client, form_data, new):
    url = reverse('news:edit', args=(News.comment.id,))
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    note_from_db = Comment.objects.get(id=new.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert new.title == note_from_db.title
    assert new.text == note_from_db.text

def test_author_can_delete_comment(author_client, comment_id):
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    assertRedirects(response, reverse('news:delete', args=comment_id))
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(not_author_client, comment_id):
    url = reverse('news:delete', args=comment_id)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1