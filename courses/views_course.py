"""
课程模块 - API 视图
实现课程 CRUD、选课、退课等功能
"""
from rest_framework import viewsets, status, decorators, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Count, F
from .models import Course, CourseEnrollment
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateSerializer,
    CourseEnrollmentSerializer,
    StudentEnrollmentSerializer
)
from .permissions import (
    IsTeacher,
    IsStudent,
    IsCourseOwnerOrReadOnly,
    IsTeacherOrStudent
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    课程 ViewSet
    提供课程的 CRUD 以及选课、退课功能
    """
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        elif self.action in ['list', 'my_courses', 'taught_courses']:
            return CourseListSerializer
        elif self.action == 'students':
            return CourseEnrollmentSerializer
        elif self.action == 'my_enrollments':
            return StudentEnrollmentSerializer
        return CourseListSerializer
    
    def get_permissions(self):
        """根据操作设置不同的权限"""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsCourseOwnerOrReadOnly]
        elif self.action in ['enroll', 'drop']:
            permission_classes = [permissions.IsAuthenticated, IsStudent]
        elif self.action == 'students':
            permission_classes = [permissions.IsAuthenticated, IsCourseOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """根据用户角色和查询参数过滤课程列表"""
        queryset = Course.objects.select_related('teacher__profile').all()
        
        search = self.request.query_params.get('search', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        """创建课程时自动绑定当前教师"""
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def enroll(self, request, pk=None):
        """选课接口"""
        course = self.get_object()
        student = request.user
        
        if not course.is_active:
            return Response({'error': '该课程已停止招生'}, status=status.HTTP_400_BAD_REQUEST)
        
        if course.enrolled_count() >= course.max_students:
            return Response({'error': '该课程已满员'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CourseEnrollment.objects.filter(student=student, course=course).exists():
            return Response({'error': '您已经选过这门课程了'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            enrollment = CourseEnrollment.objects.create(student=student, course=course)
            return Response({
                'message': '选课成功',
                'data': CourseEnrollmentSerializer(enrollment).data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': '选课失败'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def drop(self, request, pk=None):
        """退课接口"""
        course = self.get_object()
        student = request.user
        
        enrollment = CourseEnrollment.objects.filter(student=student, course=course).first()
        
        if not enrollment:
            return Response({'error': '您没有选过这门课程'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment.delete()
        return Response({'message': '退课成功'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def students(self, request, pk=None):
        """查看选课学生列表"""
        course = self.get_object()
        
        if course.teacher != request.user:
            return Response({'error': '只有课程教师才能查看学生列表'}, status=status.HTTP_403_FORBIDDEN)
        
        enrollments = CourseEnrollment.objects.filter(course=course).select_related('student__profile')
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        
        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'total_students': enrollments.count(),
            'students': serializer.data
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def is_enrolled(self, request, pk=None):
        """检查是否已选课"""
        course = self.get_object()
        
        if hasattr(request.user, 'profile') and request.user.profile.role == 'teacher':
            is_teacher = course.teacher == request.user
            return Response({
                'is_enrolled': False,
                'is_teacher': is_teacher,
                'message': '教师身份' if is_teacher else '未选课'
            })
        
        is_enrolled = CourseEnrollment.objects.filter(student=request.user, course=course).exists()
        return Response({'is_enrolled': is_enrolled, 'message': '已选课' if is_enrolled else '未选课'})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def taught_courses(self, request):
        """获取当前教师创建的所有课程"""
        courses = Course.objects.filter(teacher=request.user).select_related('teacher__profile')
        serializer = CourseListSerializer(courses, many=True)
        return Response({'total': courses.count(), 'courses': serializer.data})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def my_enrollments(self, request):
        """获取当前学生已选的所有课程"""
        enrollments = CourseEnrollment.objects.filter(student=request.user).select_related('course__teacher__profile')
        serializer = StudentEnrollmentSerializer(enrollments, many=True)
        return Response({'total': enrollments.count(), 'enrollments': serializer.data})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def available_courses(self, request):
        """获取学生可选的课程"""
        enrolled_course_ids = CourseEnrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)
        
        courses = Course.objects.filter(
            is_active=True,
            teacher__profile__role='teacher'
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            enrolled_count=Count('enrollments')
        ).filter(
            Q(enrolled_count__lt=F('max_students')) | Q(enrolled_count__isnull=True)
        ).select_related('teacher__profile')
        
        search = request.query_params.get('search', None)
        if search:
            courses = courses.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        serializer = CourseListSerializer(courses, many=True)
        return Response({'total': courses.count(), 'courses': serializer.data})
