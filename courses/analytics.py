"""
教学辅助系统 - 常用数据库查询示例
用于统计分析和易错点查询
"""

from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from courses.models import Course, Assignment, Submission, AIResult, ErrorTag, CourseEnrollment


class CourseAnalytics:
    """课程统计分析工具类"""

    @staticmethod
    def get_course_error_statistics(course_id, limit=10):
        """
        统计某课程下错误最多的知识点 Top N
        
        Args:
            course_id: 课程 ID
            limit: 返回的数量限制
            
        Returns:
            QuerySet: 包含 tag_name 和 error_count 的字典列表
        """
        return ErrorTag.objects.filter(
            ai_result__submission__assignment__course_id=course_id
        ).values(
            'tag_name'
        ).annotate(
            error_count=Count('id'),
            student_count=Count('ai_result__submission__student_id', distinct=True)
        ).order_by('-error_count')[:limit]

    @staticmethod
    def get_error_type_distribution(course_id):
        """
        统计某课程下各错误类型的分布
        
        Returns:
            QuerySet: 错误类型及其数量
        """
        return ErrorTag.objects.filter(
            ai_result__submission__assignment__course_id=course_id
        ).values('error_type').annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def get_student_error_ranking(course_id):
        """
        统计某课程下学生错误数量排名
        
        Returns:
            QuerySet: 学生 ID 及其错误数量
        """
        return ErrorTag.objects.filter(
            ai_result__submission__assignment__course_id=course_id
        ).values(
            student_id=F('ai_result__submission__student_id'),
            student_username=F('ai_result__submission__student__username')
        ).annotate(
            total_errors=Count('id'),
            avg_severity=Avg('severity')
        ).order_by('-total_errors')


class AssignmentAnalytics:
    """作业统计分析工具类"""

    @staticmethod
    def get_submission_statistics(assignment_id):
        """
        获取作业的提交统计信息
        
        Returns:
            dict: 包含提交数量、批改状态分布等统计信息
        """
        from django.db.models import Count
        
        stats = Submission.objects.filter(assignment_id=assignment_id).aggregate(
            total_submissions=Count('id'),
            pending_count=Count('id', filter=Q(status='pending')),
            grading_count=Count('id', filter=Q(status='grading')),
            completed_count=Count('id', filter=Q(status='completed')),
            failed_count=Count('id', filter=Q(status='failed')),
        )
        
        # 计算平均分
        avg_score = AIResult.objects.filter(
            submission__assignment_id=assignment_id
        ).aggregate(
            avg_score=Avg('score')
        )['avg_score']
        
        stats['average_score'] = avg_score
        
        return stats

    @staticmethod
    def get_common_errors(assignment_id, limit=5):
        """
        获取某作业最常见的错误
        
        Returns:
            QuerySet: 错误标签及其出现次数
        """
        return ErrorTag.objects.filter(
            ai_result__submission__assignment_id=assignment_id
        ).values(
            'tag_name',
            'error_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:limit]


class StudentAnalytics:
    """学生个人分析工具类"""

    @staticmethod
    def get_student_performance(student_id):
        """
        获取学生的整体表现统计
        
        Returns:
            dict: 学生的各项统计指标
        """
        from django.db.models import Avg, Count, Min, Max
        
        # 获取学生的所有提交
        submissions = Submission.objects.filter(student_id=student_id)
        
        stats = {
            'total_submissions': submissions.count(),
            'completed_submissions': submissions.filter(status='completed').count(),
            'pending_submissions': submissions.filter(status='pending').count(),
        }
        
        # 统计 AI 批改结果
        ai_results = AIResult.objects.filter(submission__student_id=student_id)
        
        if ai_results.exists():
            stats.update({
                'average_score': ai_results.aggregate(avg=Avg('score'))['avg'],
                'min_score': ai_results.aggregate(min=Min('score'))['min'],
                'max_score': ai_results.aggregate(max=Max('score'))['max'],
                'correct_rate': ai_results.filter(is_correct=True).count() / ai_results.count() * 100,
            })
        
        return stats

    @staticmethod
    def get_student_weak_points(student_id, limit=5):
        """
        获取学生的薄弱知识点（出错最多的地方）
        
        Returns:
            QuerySet: 学生的易错知识点
        """
        return ErrorTag.objects.filter(
            ai_result__submission__student_id=student_id
        ).values(
            'tag_name'
        ).annotate(
            error_count=Count('id'),
            courses_affected=Count('ai_result__submission__assignment__course_id', distinct=True)
        ).order_by('-error_count')[:limit]


class ErrorTagAnalytics:
    """错误标签深度分析工具类"""

    @staticmethod
    def get_error_trend(course_id, days=30):
        """
        获取某课程最近 N 天的错误趋势
        
        Returns:
            QuerySet: 每天的错误数量
        """
        from django.db.models import DateField
        from django.db.models.functions import TruncDate
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        return ErrorTag.objects.filter(
            ai_result__submission__assignment__course_id=course_id,
            created_at__gte=cutoff_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            error_count=Count('id')
        ).order_by('date')

    @staticmethod
    def get_severity_distribution(course_id):
        """
        获取错误严重程度分布
        
        Returns:
            QuerySet: 各严重程度的错误数量
        """
        return ErrorTag.objects.filter(
            ai_result__submission__assignment__course_id=course_id
        ).values('severity').annotate(
            count=Count('id')
        ).order_by('severity')

    @staticmethod
    def search_similar_errors(tag_name, course_id=None):
        """
        搜索相似的错误标签（用于知识点归类）
        
        Args:
            tag_name: 要搜索的标签名称
            course_id: 可选的课程 ID 限制范围
            
        Returns:
            QuerySet: 相似的错误标签
        """
        queryset = ErrorTag.objects
        
        if course_id:
            queryset = queryset.filter(
                ai_result__submission__assignment__course_id=course_id
            )
        
        return queryset.filter(
            tag_name__icontains=tag_name
        ).values(
            'tag_name'
        ).distinct().annotate(
            count=Count('id')
        ).order_by('-count')


# 使用示例
if __name__ == '__main__':
    # 示例 1: 统计课程 1 的 Top 10 易错点
    print("=== 课程 Top 10 易错点 ===")
    errors = CourseAnalytics.get_course_error_statistics(course_id=1, limit=10)
    for error in errors:
        print(f"知识点：{error['tag_name']}, 错误数：{error['error_count']}, 影响学生数：{error['student_count']}")
    
    # 示例 2: 获取作业 1 的提交统计
    print("\n=== 作业提交统计 ===")
    stats = AssignmentAnalytics.get_submission_statistics(assignment_id=1)
    print(f"总提交数：{stats['total_submissions']}")
    print(f"平均分：{stats['average_score']}")
    
    # 示例 3: 获取学生 1 的薄弱点
    print("\n=== 学生薄弱知识点 ===")
    weak_points = StudentAnalytics.get_student_weak_points(student_id=1, limit=5)
    for point in weak_points:
        print(f"知识点：{point['tag_name']}, 错误次数：{point['error_count']}")
