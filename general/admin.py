from django.contrib import admin

from django.contrib.auth.models import Group
from rangefilter.filters import DateRangeFilter

from general.filters import AuthorFilter

admin.site.unregister(Group)

from general.models import (
    Post,
    User,
    Comment,
    Reaction,
)


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    search_fields = (
        "id",
        "username",
        "email",
    )
    readonly_fields = (
        "date_joined",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("date_joined", DateRangeFilter),
    )
    fieldsets = (
        (
            "Личные данные", {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            }
        ),
        (
            "Учетные данные", {
                "fields": (
                    "username",
                    "password",
                )
            }
        ),
        (
            "Статусы", {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            }
        ),
        (
            None, {
                "fields": (
                    "friends",
                )
            }
        ),
        (
            "Даты", {
                "fields": (
                    "date_joined",
                    "last_login",
                )
            }
        )

    )


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "title",
        "body",
        "created_at",
        'get_comment_count',
    )
    list_filter = (
        AuthorFilter,
        ("created_at", DateRangeFilter),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("comments")

    def get_body(self, obj):
        max_length = 64
        if len(obj.body) > max_length:
            return obj.body[:61] + "..."
        return obj.body

    def get_comment_count(self, obj):
        return obj.comments.count()

    get_body.short_description = "body"



@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "body",
        "created_at",
    )
    list_display_links = (
        "id",
        "body",
    )
    search_fields = (
        "author__username",
        "post__title",
    )


@admin.register(Reaction)
class ReactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "value",
    )
    # autocomplete_fields = (
    #     "author",
    #     "post",
    # )
