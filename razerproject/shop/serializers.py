from rest_framework import serializers
from .models import RazerUser

class RazerUserSerializer(serializers.ModelSerializer):
    store_email = serializers.CharField(source="email")
    store_password = serializers.CharField(source="password")
    store_secret_key=serializers.CharField(source="secret_key")
    class Meta:
        model = RazerUser
        fields = ['id', 'store_email', 'store_password','store_secret_key']  
