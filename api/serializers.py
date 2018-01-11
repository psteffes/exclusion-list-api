from rest_framework import serializers
from django.core.validators import RegexValidator


class ExcListUMIDSerializer(serializers.Serializer):
    umid = serializers.CharField(
        required=True,
        validators=[RegexValidator(r'^\d{8,8}$', 'Enter a valid UMID.')],
    )


class ExcListKeySerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

