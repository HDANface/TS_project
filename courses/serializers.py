"""
序列化器模块
包含用户认证、课程管理相关序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, Course, CourseEnrollment


# ==================== 用户认证模块 ====================

class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    class Meta:
        model = UserProfile
        fields = ['role', 'real_name', 'avatar', 'phone']
        read_only_fields = ['role']


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        min_length=3,
        max_length=150,
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(required=True, write_only=True)
    real_name = serializers.CharField(required=True, max_length=100)
    role = serializers.ChoiceField(required=True, choices=UserProfile.ROLE_CHOICES)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'real_name', 'role', 'email']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        real_name = validated_data.pop('real_name')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        profile = user.profile
        profile.role = role
        profile.real_name = real_name
        profile.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义登录序列化器"""
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
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
    """用户信息序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次输入的新密码不一致'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# ==================== 课程模块 ====================

class TeacherSerializer(serializers.ModelSerializer):
    """教师信息序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']
        read_only_fields = fields


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器"""
    teacher_name = serializers.CharField(source='teacher.profile.real_name', read_only=True)
    teacher_username = serializers.CharField(source='teacher.username', read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'teacher_name', 
            'teacher_username', 'max_students', 'is_active', 
            'enrolled_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']
    
    def get_enrolled_count(self, obj):
        return obj.enrolled_count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器"""
    teacher_info = TeacherSerializer(source='teacher', read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'teacher_info',
            'max_students', 'is_active', 'enrolled_count', 'is_enrolled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']
    
    def get_enrolled_count(self, obj):
        return obj.enrolled_count()
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            if request.user.profile.role == 'student':
                return obj.enrollments.filter(student=request.user).exists()
        return None


class CourseCreateSerializer(serializers.ModelSerializer):
    """课程创建序列化器"""
    class Meta:
        model = Course
        fields = ['title', 'description', 'max_students', 'is_active']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'profile'):
            raise serializers.ValidationError("用户未认证")
        if request.user.profile.role != 'teacher':
            raise serializers.ValidationError("只有教师才能创建课程")
        course = Course.objects.create(teacher=request.user, **validated_data)
        return course


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    student_name = serializers.CharField(source='student.profile.real_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'student_name', 'student_username',
            'course', 'course_title', 'joined_at'
        ]
        read_only_fields = ['joined_at']


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """学生选课列表序列化器"""
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'course', 'joined_at']
        read_only_fields = ['joined_at']
