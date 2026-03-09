"""
教学辅助系统 - Django Admin 配置
提供便捷的后台管理界面
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Course, CourseEnrollment, Assignment, Submission, AIResult, ErrorTag


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """课程管理配置"""
    list_display = [
        'title',
        'teacher',
        'enrolled_count_display',
        'max_students',
        'is_active',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'teacher')
        }),
        ('设置', {
            'fields': ('max_students', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def enrolled_count_display(self, obj):
        """显示已选课学生数量"""
        return obj.enrolled_count()
    enrolled_count_display.short_description = '已选课学生'


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """课程选课记录管理配置"""
    list_display = ['student', 'course', 'joined_at']
    list_filter = ['course', 'joined_at']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['joined_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """作业管理配置"""
    list_display = [
        'title',
        'course',
        'due_date',
        'max_score',
        'is_published',
        'submission_count_display',
        'created_at',
    ]
    list_filter = ['is_published', 'allow_late_submission', 'course']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'course', 'description')
        }),
        ('要求', {
            'fields': ('requirements', 'max_score')
        }),
        ('时间设置', {
            'fields': ('due_date', 'allow_late_submission')
        }),
        ('发布设置', {
            'fields': ('is_published',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def submission_count_display(self, obj):
        """显示提交数量"""
        return obj.submission_count()
    submission_count_display.short_description = '提交数量'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """作业提交管理配置"""
    list_display = [
        'student',
        'assignment',
        'status',
        'is_late',
        'submitted_at',
        'has_ai_result',
    ]
    list_filter = ['status', 'is_late', 'assignment']
    search_fields = ['student__username', 'assignment__title']
    readonly_fields = ['submitted_at', 'created_at', 'updated_at']
    date_hierarchy = 'submitted_at'
    
    def has_ai_result(self, obj):
        """显示是否有 AI 批改结果"""
        return hasattr(obj, 'ai_result')
    has_ai_result.boolean = True
    has_ai_result.short_description = '已批改'


@admin.register(AIResult)
class AIResultAdmin(admin.ModelAdmin):
    """AI 批改结果管理配置"""
    list_display = [
        'submission_link',
        'student_name',
        'score',
        'is_correct',
        'error_count',
        'graded_at',
        'model_version',
    ]
    list_filter = ['is_correct', 'graded_at', 'model_version']
    search_fields = ['submission__student__username', 'feedback']
    readonly_fields = ['graded_at', 'created_at', 'updated_at']
    date_hierarchy = 'graded_at'
    
    fieldsets = (
        ('评分信息', {
            'fields': ('submission', 'is_correct', 'score')
        }),
        ('AI 反馈', {
            'fields': ('feedback', 'analysis')
        }),
        ('模型信息', {
            'fields': ('model_version', 'raw_response'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('graded_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def submission_link(self, obj):
        """显示提交链接"""
        return format_html(
            '<a href="/admin/courses/submission/{}/change/">{}</a>',
            obj.submission.id,
            str(obj.submission)
        )
    submission_link.short_description = '作业提交'
    
    def student_name(self, obj):
        """显示学生姓名"""
        return obj.submission.student.username
    student_name.short_description = '学生'
    
    def error_count(self, obj):
        """显示错误标签数量"""
        return obj.error_tags.count()
    error_count.short_description = '错误数'


@admin.register(ErrorTag)
class ErrorTagAdmin(admin.ModelAdmin):
    """错误知识点标签管理配置"""
    list_display = [
        'tag_name',
        'error_type',
        'severity',
        'student_name',
        'course_name',
        'line_number',
        'created_at',
    ]
    list_filter = ['severity', 'error_type', 'tag_name']
    search_fields = ['tag_name', 'error_type', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def student_name(self, obj):
        """显示学生姓名"""
        return obj.ai_result.submission.student.username
    student_name.short_description = '学生'
    
    def course_name(self, obj):
        """显示课程名称"""
        return obj.ai_result.submission.assignment.course.title
    course_name.short_description = '课程'


# 自定义 Admin 站点标题和副标题
admin.site.site_header = '教学辅助系统管理后台'
admin.site.site_title = '教学辅助系统'
admin.site.index_title = '欢迎使用教学辅助系统管理平台'
