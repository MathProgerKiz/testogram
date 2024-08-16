from rest_framework import status
from rest_framework.test import APITestCase

from general.factories import UserFactory, ChatFactory, MessageFactory


class ChatTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/chats/"

    def test_get_chat_list(self):
        # создаем 3 пользователей, с которыми у нас будут чаты.
        user_1 = UserFactory()
        user_2 = UserFactory()
        user_3 = UserFactory()

        # создаем чаты с ними
        chat_1 = ChatFactory(user_1=self.user, user_2=user_1)
        chat_2 = ChatFactory(user_1=self.user, user_2=user_2)
        # пусть в третьем чате наш пользователь будет в роли user_2.
        chat_3 = ChatFactory(user_1=user_3, user_2=self.user)

        # в каждом чате создадим по одному сообщению.
        # чтобы протестировать правильность сортировки чатов
        # мы нарочно создадим сначала сообщение в третьем чате,
        # а затем во втором.
        mes_1 = MessageFactory(author=self.user, chat=chat_1)
        mes_3 = MessageFactory(author=self.user, chat=chat_3)
        # также одно из сообщения создаем от собеседника.
        mes_2 = MessageFactory(author=user_2, chat=chat_2)

        # создадим пачку чужих сообщений в чужих чатах.
        # они нужны для того, чтобы мы убедились,
        # что получаем только свои чаты и сообщения.
        MessageFactory.create_batch(10)

        with self.assertNumQueries(2):
            response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # чаты сортируются по дате последнего сообщения.
        # поэтому порядок чатов должен быть такой: chat_2, chat_3, chat_1.
        # создаем список ID чатов из response.
        response_chat_ids = [
            chat["id"]
            for chat
            in response.data["results"]
        ]
        # создаем список с ожидаемыми ID
        expected_chat_ids = [chat_2.pk, chat_3.pk, chat_1.pk]
        self.assertListEqual(response_chat_ids, expected_chat_ids)

        # теперь проверяем каждый отдельный чат.
        chat_2_expected_data = {
            "id": chat_2.pk,
            "companion_name": f"{user_2.first_name} {user_2.last_name}",
            "last_message_content": mes_2.content,
            "last_message_datetime": mes_2.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(
            response.data["results"][0],
            chat_2_expected_data,
        )

        chat_3_expected_data = {
            "id": chat_3.pk,
            "companion_name": f"{user_3.first_name} {user_3.last_name}",
            "last_message_content": mes_3.content,
            "last_message_datetime": mes_3.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(
            response.data["results"][1],
            chat_3_expected_data,
        )

        chat_1_expected_data = {
            "id": chat_1.pk,
            "companion_name": f"{user_1.first_name} {user_1.last_name}",
            "last_message_content": mes_1.content,
            "last_message_datetime": mes_1.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(
            response.data["results"][2],
            chat_1_expected_data,
        )