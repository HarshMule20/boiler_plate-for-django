from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'mobile', 'gender', 'birth_date', 'password',
                  'created_at', 'updated_at', 'added_by']

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'mobile': instance.mobile,
            'gender': instance.gender,
            'birth_date': instance.birth_date,
            'created_at': instance.created_at
        }
