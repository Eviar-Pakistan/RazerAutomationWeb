from rest_framework import serializers
from .models import RazerUser

class RazerUserSerializer(serializers.ModelSerializer):
    store_email = serializers.CharField(source="email")
    store_password = serializers.CharField(source="password")
    class Meta:
        model = RazerUser
        fields = ['id', 'store_email', 'store_password']  
