"""
用户认证模块 - 序列化器
包含用户注册、登录相关序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    用于序列化 UserProfile 模型
    """
    class Meta:
        model = UserProfile
        fields = ['role', 'real_name', 'avatar', 'phone']
        read_only_fields = ['role']


class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    处理用户注册逻辑，包括密码验证和加密
    """
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        min_length=3,
        max_length=150,
        help_text='用户名（3-150 字符）'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        validators=[validate_password],
        help_text='密码（至少 6 个字符）'
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text='确认密码'
    )
    real_name = serializers.CharField(
        required=True,
        max_length=100,
        help_text='真实姓名'
    )
    role = serializers.ChoiceField(
        required=True,
        choices=UserProfile.ROLE_CHOICES,
        help_text='角色：student 或 teacher'
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text='邮箱地址（可选）'
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'real_name', 'role', 'email']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        """
        验证器 - 校验两次密码是否一致
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        return attrs

    def create(self, validated_data):
        """
        创建用户 - 对密码进行哈希加密
        """
        # 提取角色信息
        role = validated_data.pop('role')
        real_name = validated_data.pop('real_name')
        
        # 创建用户（密码会自动哈希）
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        # 更新用户资料
        profile = user.profile
        profile.role = role
        profile.real_name = real_name
        profile.save()
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义登录序列化器
    在返回 JWT token 的同时，附带用户基本信息
    """
    
    def validate(self, attrs):
        """
        验证用户名密码，并在成功后添加用户信息
        """
        # 调用父类验证方法（验证用户名密码）
        data = super().validate(attrs)
        
        # 获取用户对象
        user = self.user
        
        # 添加用户基本信息
        data.update({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'real_name': user.profile.real_name,
                'role': user.profile.role,
                'avatar': user.profile.avatar,
                'phone': user.profile.phone,
            }
        })
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器
    用于展示用户完整信息
    """
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text='原密码'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        validators=[validate_password],
        help_text='新密码'
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text='确认新密码'
    )

    def validate(self, attrs):
        """
        验证新密码是否一致
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        return attrs

    def validate_old_password(self, value):
        """
        验证原密码是否正确
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value

    def save(self):
        """
        保存新密码
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
