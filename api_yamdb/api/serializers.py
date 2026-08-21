import re

from rest_framework import serializers

from reviews.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Username не соответствует шаблону'
            )
        return value


class SignUpSerializer(UsernameSerializer):
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    def validate(self, data):
        username = data['username']
        email = data['email']
        if User.objects.filter(
            username=username
        ).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Этот username уже занят.'}
            )
        if User.objects.filter(
            email=email
        ).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Этот email уже занят.'}
            )
        return data


class TokenSerializer(UsernameSerializer):
    confirmation_code = serializers.CharField()
