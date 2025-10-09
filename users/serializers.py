from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


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
        instance.payment_status = validated_data.get("payment_status", instance.payment_status)
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


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'subdomain', 'secret_key', 'name', 'role', 'payment_status', 'is_active',
                  'is_superuser',)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'password', 'subdomain']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'subdomain', 'payment_status', 'is_active']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.name = validated_data.get('name', instance.name)
        instance.role = validated_data.get('role', instance.role)
        instance.subdomain = validated_data.get('subdomain', instance.subdomain)
        instance.payment_status = validated_data.get('payment_status', instance.payment_status)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
