from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "username", "role", "payment_status")
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def validate_username(self, value):
        return value

    def update(self, instance, validated_data):
        instance.name = (validated_data.get("name", instance.name))
        instance.username = (validated_data.get("username", instance.username))
        instance.role = validated_data.get("role", instance.role)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Username va password kiritilishi shart.")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Username yoki password noto‘g‘ri.")

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Invalid or expired token.'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
