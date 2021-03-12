from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.settings import api_settings

from speshalgram.accounts.models import Subscription, User


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            ASCIIUsernameValidator()(username)
        except DjangoValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"username": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )
        
        user = User(**attrs)

        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    nfollowers = serializers.IntegerField(required=False, read_only=True)
    nfollows = serializers.IntegerField(required=False, read_only=True)
    followed_by_me_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username',  
            'first_name', 
            'last_name', 
            'description', 
            'avatar', 
            'is_opened',
            'nfollowers',
            'nfollows',
            'followed_by_me_status'
        ]
    
    def get_followed_by_me_status(self, obj):
        status = getattr(obj, 'followed_by_me_status', None)

        if request := self.context.get('request'):
            if obj.username == request.user.username:
                return 'self'
            elif status in {Subscription.ACCEPTED, Subscription.PENDING}:
                return dict(Subscription.STATUSES)[status]
        
        return None
