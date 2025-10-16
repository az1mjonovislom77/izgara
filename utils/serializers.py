import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import serializers
from utils.models import QrCode
from users.models import User
from django.utils import timezone


class QrCodeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

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
    total_scans = serializers.SerializerMethodField()
    daily_scans = serializers.SerializerMethodField()
    monthly_scans = serializers.SerializerMethodField()
    yearly_scans = serializers.SerializerMethodField()

    class Meta:
        model = QrCode
        fields = [
            'id', 'user', 'link', 'image', 'created',
            'scan_count', 'last_scanned_ip',
            'total_scans', 'daily_scans', 'monthly_scans', 'yearly_scans'
        ]
        read_only_fields = fields

    def get_total_scans(self, obj):
        return obj.scans.count()

    def get_daily_scans(self, obj):
        today = timezone.now().date()
        return obj.scans.filter(created__date=today).count()

    def get_monthly_scans(self, obj):
        now = timezone.now()
        return obj.scans.filter(created__year=now.year, created__month=now.month).count()

    def get_yearly_scans(self, obj):
        now = timezone.now()
        return obj.scans.filter(created__year=now.year).count()
