from rest_framework import serializers
from django.core.validators import RegexValidator

class ExcListFindSerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    ou = serializers.CharField(required=False)

    umid = serializers.CharField(
        required=True,
        validators=[RegexValidator(r'^\d{8,8}$', 'Enter a valid UMID.')],
    )


class ExcListAddDeleteSerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    ou = serializers.CharField(required=False)
