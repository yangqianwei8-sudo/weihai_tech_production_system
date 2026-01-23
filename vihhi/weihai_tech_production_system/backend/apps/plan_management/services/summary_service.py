"""
工作总结服务

生成周报和月报，包括：
- 目标更新进度
- 计划完成情况
- 统计分析
"""
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..models import StrategicGoal, Plan, GoalProgressRecord, PlanProgressRecord
from ..notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


def generate_weekly_summary(user, week_start_date=None) -> Dict[str, Any]:
    """
    生成用户的上周工作总结
    
    Args:
        user: User 对象
        week_start_date: 上周一的日期，如果为None则自动计算
    
    Returns:
        Dict: 周报数据
    """
    if week_start_date is None:
        # 计算上周一
        today = timezone.now().date()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        week_start_date = last_monday
    
    week_end_date = week_start_date + timedelta(days=6)
    week_start_datetime = timezone.make_aware(
        datetime.combine(week_start_date, datetime.min.time())
    )
    week_end_datetime = timezone.make_aware(
        datetime.combine(week_end_date, datetime.max.time())
    )
    
    # 1. 目标更新进度
    goal_updates = GoalProgressRecord.objects.filter(
        goal__owner=user,
        recorded_time__gte=week_start_datetime,
        recorded_time__lte=week_end_datetime
    ).select_related('goal').order_by('-recorded_time')
    
    goal_summary = []
    for update in goal_updates:
        goal_summary.append({
            'goal_name': update.goal.name,
            'completion_rate': float(update.completion_rate),
            'current_value': float(update.current_value),
            'target_value': float(update.goal.target_value),
            'update_time': update.recorded_time.strftime('%Y-%m-%d %H:%M'),
            'description': update.progress_description[:100]  # 截取前100字符
        })
    
    # 2. 周计划任务完成情况
    weekly_plans = Plan.objects.filter(
        owner=user,
        plan_period='weekly',
        start_time__gte=week_start_datetime,
        start_time__lte=week_end_datetime
    ).select_related('related_goal')
    
    plan_summary = []
    completed_count = 0
    in_progress_count = 0
    overdue_count = 0
    
    for plan in weekly_plans:
        status_text = plan.get_status_display()
        if plan.status == 'completed':
            completed_count += 1
        elif plan.status == 'in_progress':
            in_progress_count += 1
        elif plan.is_overdue:
            overdue_count += 1
        
        plan_summary.append({
            'plan_name': plan.name,
            'status': status_text,
            'progress': float(plan.progress),
            'is_overdue': plan.is_overdue,
            'start_time': plan.start_time.strftime('%Y-%m-%d'),
            'end_time': plan.end_time.strftime('%Y-%m-%d'),
        })
    
    # 3. 统计汇总
    total_plans = len(plan_summary)
    completion_rate = (completed_count / total_plans * 100) if total_plans > 0 else 0
    
    return {
        'user': user,
        'week_start': week_start_date.strftime('%Y-%m-%d'),
        'week_end': week_end_date.strftime('%Y-%m-%d'),
        'goal_updates': goal_summary,
        'goal_updates_count': len(goal_summary),
        'plans': plan_summary,
        'total_plans': total_plans,
        'completed_plans': completed_count,
        'in_progress_plans': in_progress_count,
        'overdue_plans': overdue_count,
        'completion_rate': round(completion_rate, 2),
    }


def generate_monthly_summary(user, month_start_date=None) -> Dict[str, Any]:
    """
    生成用户的上月工作总结
    
    Args:
        user: User 对象
        month_start_date: 上月1日的日期，如果为None则自动计算
    
    Returns:
        Dict: 月报数据
    """
    if month_start_date is None:
        # 计算上月1日
        today = timezone.now().date()
        if today.month == 1:
            month_start_date = datetime(today.year - 1, 12, 1).date()
        else:
            month_start_date = datetime(today.year, today.month - 1, 1).date()
    
    # 计算上月最后一天
    if month_start_date.month == 12:
        month_end_date = datetime(month_start_date.year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end_date = datetime(month_start_date.year, month_start_date.month + 1, 1).date() - timedelta(days=1)
    
    month_start_datetime = timezone.make_aware(
        datetime.combine(month_start_date, datetime.min.time())
    )
    month_end_datetime = timezone.make_aware(
        datetime.combine(month_end_date, datetime.max.time())
    )
    
    # 1. 目标更新进度
    goal_updates = GoalProgressRecord.objects.filter(
        goal__owner=user,
        recorded_time__gte=month_start_datetime,
        recorded_time__lte=month_end_datetime
    ).select_related('goal').order_by('-recorded_time')
    
    goal_summary = []
    for update in goal_updates:
        goal_summary.append({
            'goal_name': update.goal.name,
            'completion_rate': float(update.completion_rate),
            'current_value': float(update.current_value),
            'target_value': float(update.goal.target_value),
            'update_time': update.recorded_time.strftime('%Y-%m-%d %H:%M'),
            'description': update.progress_description[:100]
        })
    
    # 2. 月度计划完成情况
    monthly_plans = Plan.objects.filter(
        owner=user,
        plan_period='monthly',
        start_time__gte=month_start_datetime,
        start_time__lte=month_end_datetime
    ).select_related('related_goal')
    
    plan_summary = []
    completed_count = 0
    in_progress_count = 0
    overdue_count = 0
    
    for plan in monthly_plans:
        status_text = plan.get_status_display()
        if plan.status == 'completed':
            completed_count += 1
        elif plan.status == 'in_progress':
            in_progress_count += 1
        elif plan.is_overdue:
            overdue_count += 1
        
        plan_summary.append({
            'plan_name': plan.name,
            'status': status_text,
            'progress': float(plan.progress),
            'is_overdue': plan.is_overdue,
            'start_time': plan.start_time.strftime('%Y-%m-%d'),
            'end_time': plan.end_time.strftime('%Y-%m-%d'),
        })
    
    # 3. 统计汇总
    total_plans = len(plan_summary)
    completion_rate = (completed_count / total_plans * 100) if total_plans > 0 else 0
    
    return {
        'user': user,
        'month': month_start_date.strftime('%Y年%m月'),
        'month_start': month_start_date.strftime('%Y-%m-%d'),
        'month_end': month_end_date.strftime('%Y-%m-%d'),
        'goal_updates': goal_summary,
        'goal_updates_count': len(goal_summary),
        'plans': plan_summary,
        'total_plans': total_plans,
        'completed_plans': completed_count,
        'in_progress_plans': in_progress_count,
        'overdue_plans': overdue_count,
        'completion_rate': round(completion_rate, 2),
    }


def format_weekly_summary_text(summary: Dict[str, Any]) -> str:
    """格式化周报为文本"""
    lines = []
    lines.append(f"📊 周工作总结 ({summary['week_start']} 至 {summary['week_end']})")
    lines.append("=" * 60)
    lines.append("")
    
    # 目标更新
    lines.append("🎯 目标更新进度：")
    if summary['goal_updates_count'] > 0:
        for update in summary['goal_updates'][:5]:  # 最多显示5条
            lines.append(f"  • {update['goal_name']}: {update['completion_rate']}% ({update['update_time']})")
    else:
        lines.append("  本周无目标更新记录")
    lines.append("")
    
    # 计划完成情况
    lines.append("📋 周计划完成情况：")
    lines.append(f"  总计划数：{summary['total_plans']}")
    lines.append(f"  已完成：{summary['completed_plans']}")
    lines.append(f"  进行中：{summary['in_progress_plans']}")
    lines.append(f"  已逾期：{summary['overdue_plans']}")
    lines.append(f"  完成率：{summary['completion_rate']}%")
    lines.append("")
    
    if summary['total_plans'] > 0:
        lines.append("计划详情：")
        for plan in summary['plans'][:10]:  # 最多显示10条
            status_icon = "✅" if plan['status'] == '已完成' else "⏳" if plan['status'] == '执行中' else "⚠️"
            lines.append(f"  {status_icon} {plan['plan_name']} ({plan['status']}, 进度: {plan['progress']}%)")
    
    return "\n".join(lines)


def format_monthly_summary_text(summary: Dict[str, Any]) -> str:
    """格式化月报为文本"""
    lines = []
    lines.append(f"📊 月工作总结 ({summary['month']})")
    lines.append("=" * 60)
    lines.append("")
    
    # 目标更新
    lines.append("🎯 目标更新进度：")
    if summary['goal_updates_count'] > 0:
        for update in summary['goal_updates'][:10]:  # 最多显示10条
            lines.append(f"  • {update['goal_name']}: {update['completion_rate']}% ({update['update_time']})")
    else:
        lines.append("  本月无目标更新记录")
    lines.append("")
    
    # 计划完成情况
    lines.append("📋 月度计划完成情况：")
    lines.append(f"  总计划数：{summary['total_plans']}")
    lines.append(f"  已完成：{summary['completed_plans']}")
    lines.append(f"  进行中：{summary['in_progress_plans']}")
    lines.append(f"  已逾期：{summary['overdue_plans']}")
    lines.append(f"  完成率：{summary['completion_rate']}%")
    lines.append("")
    
    if summary['total_plans'] > 0:
        lines.append("计划详情：")
        for plan in summary['plans'][:20]:  # 最多显示20条
            status_icon = "✅" if plan['status'] == '已完成' else "⏳" if plan['status'] == '执行中' else "⚠️"
            lines.append(f"  {status_icon} {plan['plan_name']} ({plan['status']}, 进度: {plan['progress']}%)")
    
    return "\n".join(lines)


def send_weekly_summary_to_user(user):
    """发送周报给用户及其上级"""
    try:
        summary = generate_weekly_summary(user)
        summary_text = format_weekly_summary_text(summary)
        
        # 发送给用户
        safe_approval_notification(
            user=user,
            title='[周报] 上周工作总结',
            content=summary_text,
            object_type='summary',
            object_id='weekly',
            event='weekly_summary',
            is_read=False
        )
        
        # 发送给上级（如果有）
        # 简化实现：查找用户的上级（通过部门关系或其他方式）
        # 这里暂时跳过，后续可根据实际业务逻辑实现
        
        return True
    except Exception as e:
        logger.error(f"发送周报给用户 {user.username} 失败：{str(e)}", exc_info=True)
        return False


def send_monthly_summary_to_user(user):
    """发送月报给用户及其上级"""
    try:
        summary = generate_monthly_summary(user)
        summary_text = format_monthly_summary_text(summary)
        
        # 发送给用户
        safe_approval_notification(
            user=user,
            title='[月报] 上月工作总结',
            content=summary_text,
            object_type='summary',
            object_id='monthly',
            event='monthly_summary',
            is_read=False
        )
        
        # 发送给上级（如果有）
        # 简化实现：查找用户的上级（通过部门关系或其他方式）
        # 这里暂时跳过，后续可根据实际业务逻辑实现
        
        return True
    except Exception as e:
        logger.error(f"发送月报给用户 {user.username} 失败：{str(e)}", exc_info=True)
        return False
