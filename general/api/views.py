from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from general.api.serializers import UserRegistrationSerializer, UserListSerializer, UserRetrieveSerializer, \
    PostListSerializer, PostRetrieveSerializer, PostCreateUpdateSerializer
from general.models import User, Post
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet):

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action in ["retrieve", "me"]:
            return UserRetrieveSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def friends(self, request, pk=None):
        user = self.get_object()
        queryset = self.filter_queryset(
            self.get_queryset().filter(friends=user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_friend(self, request, pk=None):
        user = self.get_object()
        request.user.friends.add(user)
        return Response("Friend added")

    @action(detail=True, methods=["post"])
    def remove_friend(self, request, pk=None):
        user = self.get_object()
        request.user.friends.remove(user)
        return Response("Friend removed")

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related(
            "friends",
        ).order_by("-id")
        return queryset


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostCreateUpdateSerializer
