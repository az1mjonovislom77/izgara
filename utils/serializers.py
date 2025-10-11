from rest_framework import serializers

from utils.models import QrCode


class QrCodeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = QrCode
        fields = ['id', 'user', 'link', 'image', 'created']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None
