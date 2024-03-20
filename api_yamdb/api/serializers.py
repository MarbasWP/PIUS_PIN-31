from abc import ABC

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator
from users.models import User


class AuthSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+\Z",
        required=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    def validate(self, data):
        if data.get("username") == "me":
            raise serializers.ValidationError("Ошибка: недопустимое имя")

        return data


class GetJWTTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        if not User.objects.filter(username=data.get("username")).exists():
            raise NotFound("Ошибка: не верный username")
        if not User.objects.filter(
            password=data.get("confirmation_code")
        ).exists():
            raise serializers.ValidationError(
                "Ошибка: не верный confirmation_code"
            )
        return data


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
