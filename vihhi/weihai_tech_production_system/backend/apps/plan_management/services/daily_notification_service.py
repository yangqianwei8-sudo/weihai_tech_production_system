"""
每日通知服务

生成每日通知内容，包括：
1. 昨日战报：已完成任务和提前完成表扬
2. 今日战场：今日待办任务，高亮逾期任务
3. 风险预警：目标滞后、即将到期、项目阻塞、下属逾期等
"""
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..models import StrategicGoal, Plan, GoalProgressRecord
from ..notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


def generate_daily_notification_content(user) -> Dict[str, Any]:
    """
    生成用户的每日通知内容
    
    Args:
        user: User 对象
    
    Returns:
        Dict: 通知内容
    """
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    three_days_later = today + timedelta(days=3)
    
    # ========== 1. 昨日战报 ==========
    yesterday_start = timezone.make_aware(datetime.combine(yesterday, datetime.min.time()))
    yesterday_end = timezone.make_aware(datetime.combine(yesterday, datetime.max.time()))
    
    # 昨天完成的任务
    completed_plans_yesterday = Plan.objects.filter(
        owner=user,
        status='completed',
        completed_at__gte=yesterday_start,
        completed_at__lte=yesterday_end
    ).select_related('related_goal')
    
    # 提前完成的任务（完成时间早于结束时间，且昨天完成的）
    # 简化实现：查找昨天完成且完成时间早于结束时间的计划
    early_completed_plans = []
    for plan in completed_plans_yesterday:
        if plan.completed_at and plan.end_time:
            if plan.completed_at < plan.end_time:
                days_early = (plan.end_time.date() - plan.completed_at.date()).days
                if days_early > 0:
                    early_completed_plans.append(plan)
    
    yesterday_report = {
        'completed_tasks': [],
        'early_completed_tasks': [],
    }
    
    for plan in completed_plans_yesterday:
        days_early = 0
        if plan.completed_at and plan.end_time:
            days_early = (plan.end_time.date() - plan.completed_at.date()).days
        
        yesterday_report['completed_tasks'].append({
            'name': plan.name,
            'completed_at': plan.completed_at.strftime('%Y-%m-%d %H:%M') if plan.completed_at else '',
            'days_early': days_early,
        })
    
    for plan in early_completed_plans[:5]:  # 最多显示5个
        if plan.completed_at and plan.end_time:
            days_early = (plan.end_time.date() - plan.completed_at.date()).days
            if days_early > 0:
                yesterday_report['early_completed_tasks'].append({
                    'name': plan.name,
                    'days_early': days_early,
                    'completed_at': plan.completed_at.strftime('%Y-%m-%d %H:%M') if plan.completed_at else '',
                })
    
    # ========== 2. 今日战场 ==========
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    # 所有截止到今天且状态未完成的任务
    today_tasks = Plan.objects.filter(
        owner=user,
        status__in=['accepted', 'in_progress'],
        end_time__lte=today_end
    ).select_related('related_goal')
    
    today_battlefield = {
        'all_tasks': [],
        'overdue_tasks': [],
        'normal_tasks': [],
    }
    
    for plan in today_tasks:
        is_overdue = plan.is_overdue or (plan.end_time.date() < today)
        task_info = {
            'name': plan.name,
            'status': plan.get_status_display(),
            'progress': float(plan.progress),
            'end_time': plan.end_time.strftime('%Y-%m-%d'),
            'is_overdue': is_overdue,
        }
        
        today_battlefield['all_tasks'].append(task_info)
        if is_overdue:
            today_battlefield['overdue_tasks'].append(task_info)
        else:
            today_battlefield['normal_tasks'].append(task_info)
    
    # ========== 3. 风险预警 ==========
    risks = {
        'lagging_goals': 0,
        'upcoming_tasks': 0,
        'blocked_tasks': [],  # 项目阻塞任务（简化实现）
        'subordinate_overdue': [],  # 下属逾期任务（简化实现）
    }
    
    # 目标进度滞后（最近一次更新超过7天）
    seven_days_ago = now - timedelta(days=7)
    user_goals = StrategicGoal.objects.filter(
        owner=user,
        status__in=['accepted', 'in_progress']
    )
    
    for goal in user_goals:
        last_update = GoalProgressRecord.objects.filter(
            goal=goal
        ).order_by('-recorded_time').first()
        
        if not last_update or last_update.recorded_time < seven_days_ago:
            risks['lagging_goals'] += 1
    
    # 即将在三天内到期的任务
    upcoming_tasks = Plan.objects.filter(
        owner=user,
        status__in=['accepted', 'in_progress'],
        end_time__gte=today_start,
        end_time__lte=timezone.make_aware(datetime.combine(three_days_later, datetime.max.time()))
    ).count()
    risks['upcoming_tasks'] = upcoming_tasks
    
    # 项目阻塞任务（简化实现：查找关联项目的计划，如果计划逾期则视为阻塞）
    # 这里简化处理，后续可根据实际业务逻辑完善
    
    # 下属逾期任务（简化实现：查找用户作为responsible_person的计划）
    subordinate_plans = Plan.objects.filter(
        responsible_person=user,
        status__in=['in_progress'],
        is_overdue=True
    ).select_related('owner')
    
    subordinate_dict = {}
    for plan in subordinate_plans:
        if plan.owner:
            subordinate_name = plan.owner.get_full_name() or plan.owner.username
            if subordinate_name not in subordinate_dict:
                subordinate_dict[subordinate_name] = 0
            subordinate_dict[subordinate_name] += 1
    
    risks['subordinate_overdue'] = [
        {'name': name, 'count': count}
        for name, count in subordinate_dict.items()
    ]
    
    return {
        'yesterday_report': yesterday_report,
        'today_battlefield': today_battlefield,
        'risks': risks,
    }


def format_daily_notification_text(content: Dict[str, Any]) -> str:
    """格式化每日通知为文本"""
    lines = []
    lines.append("📢 每日工作通知")
    lines.append("=" * 60)
    lines.append("")
    
    # 昨日战报
    lines.append("🎉 昨日战报：")
    yesterday = content['yesterday_report']
    
    if yesterday['completed_tasks']:
        lines.append("  已完成任务：")
        for task in yesterday['completed_tasks'][:10]:  # 最多显示10个
            lines.append(f"    ✅ {task['name']} ({task['completed_at']})")
    else:
        lines.append("  昨日无完成任务")
    
    if yesterday['early_completed_tasks']:
        lines.append("")
        lines.append("  🌟 提前完成（表现出色）：")
        for task in yesterday['early_completed_tasks']:
            lines.append(f"    ⭐ {task['name']} 提前{task['days_early']}天完成！")
    
    lines.append("")
    
    # 今日战场
    lines.append("⚔️ 今日战场：")
    battlefield = content['today_battlefield']
    
    if battlefield['overdue_tasks']:
        lines.append("  ⚠️ 已逾期任务（高亮）：")
        for task in battlefield['overdue_tasks'][:10]:
            lines.append(f"    🔴 {task['name']} (进度: {task['progress']}%, 截止: {task['end_time']})")
        lines.append("")
    
    if battlefield['normal_tasks']:
        lines.append("  📋 待完成任务：")
        for task in battlefield['normal_tasks'][:10]:
            lines.append(f"    ⚪ {task['name']} (进度: {task['progress']}%, 截止: {task['end_time']})")
    
    if not battlefield['all_tasks']:
        lines.append("  今日无待办任务")
    
    lines.append("")
    
    # 风险预警
    lines.append("⚠️ 风险预警：")
    risks = content['risks']
    
    if risks['lagging_goals'] > 0:
        lines.append(f"  • 您有{risks['lagging_goals']}个目标进度已滞后，点击查看。")
    
    if risks['upcoming_tasks'] > 0:
        lines.append(f"  • 您有{risks['upcoming_tasks']}个任务即将在三天内到期。")
    
    if risks['blocked_tasks']:
        for blocked in risks['blocked_tasks']:
            lines.append(f"  • 您负责的{blocked['project']}关键路径任务已被阻塞{blocked['days']}天，需立即关注。")
    
    if risks['subordinate_overdue']:
        lines.append("  上级关注：")
        for sub in risks['subordinate_overdue']:
            lines.append(f"    • 您的下属{sub['name']}有{sub['count']}项任务已逾期，请跟进。")
    
    if risks['lagging_goals'] == 0 and risks['upcoming_tasks'] == 0 and not risks['blocked_tasks'] and not risks['subordinate_overdue']:
        lines.append("  暂无风险预警")
    
    return "\n".join(lines)


def send_daily_notification(user):
    """发送每日通知给用户"""
    try:
        content = generate_daily_notification_content(user)
        notification_text = format_daily_notification_text(content)
        
        safe_approval_notification(
            user=user,
            title='[每日通知] 工作提醒',
            content=notification_text,
            object_type='notification',
            object_id='daily',
            event='daily_notification',
            is_read=False
        )
        
        return True
    except Exception as e:
        logger.error(f"发送每日通知给用户 {user.username} 失败：{str(e)}", exc_info=True)
        return False
