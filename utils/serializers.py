import uuid
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
from rest_framework import serializers
from utils.models import QrCode
from users.models import User


class QrCodeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = QrCode
        fields = ['id', 'user', 'link', 'image', 'created']
        read_only_fields = ['image', 'created']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        if not request:
            return attrs

        current_user = request.user
        target_user = attrs.get('user')

        if current_user.role == User.UserRoles.CAFE:
            attrs['user'] = current_user
            target_user = current_user

        elif current_user.role == User.UserRoles.ADMIN:
            if not target_user:
                raise serializers.ValidationError(
                    {"user": "Admin uchun 'user' maydoni majburiy."}
                )

        if QrCode.objects.filter(user=target_user).exists():
            raise serializers.ValidationError(
                {"user": f"{target_user.username} foydalanuvchida allaqachon QR code mavjud."}
            )

        return attrs


class QrCodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = ['link']

    def update(self, instance, validated_data):
        new_link = validated_data.get('link', instance.link)

        if new_link != instance.link:
            instance.link = new_link

            if instance.image:
                instance.image.delete(save=False)

            qr_img = qrcode.make(new_link)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f"qr_{instance.user.username}_{uuid.uuid4().hex[:8]}.png"
            instance.image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        instance.save()
        return instance


class QrCodeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = '__all__'



