"""
计划管理信号监听

实现目标/计划状态变更时的自动动作：
1. 目标发布后，为员工创建目标分解待办
2. 公司计划发布后，为员工创建个人计划创建待办
3. 目标/计划进度更新后，通知上级
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from .models import StrategicGoal, Plan, GoalProgressRecord, PlanProgressRecord, Todo
from .notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


def handle_goal_published(goal):
    """
    处理目标发布后的动作
    
    当目标状态变为published时：
    - 如果是公司目标，通知所有员工并创建目标分解待办
    - 如果是个人目标，通知目标所有者
    """
    try:
        if goal.status == 'published' and goal.published_at:
            # 检查是否已有相关的待办事项（避免重复创建）
            existing_todos = Todo.objects.filter(
                related_goal=goal,
                todo_type='goal_decomposition'
            ).exists()
            
            if existing_todos:
                return  # 已存在待办，跳过
            
            # 计算截止时间：当前季度起始月10日 09:00
            now = timezone.now()
            current_month = now.month
            current_year = now.year
            
            # 确定季度起始月
            if current_month in [1, 2, 3]:
                quarter_start_month = 1
            elif current_month in [4, 5, 6]:
                quarter_start_month = 4
            elif current_month in [7, 8, 9]:
                quarter_start_month = 7
            else:
                quarter_start_month = 10
            
            deadline = timezone.make_aware(
                datetime(current_year, quarter_start_month, 10, 9, 0, 0)
            )
            
            if goal.level == 'company':
                # 公司目标：通知所有员工并创建目标分解待办
                # 简化实现：通知所有活跃用户（后续可优化为按部门/角色筛选）
                users = User.objects.filter(is_active=True)
                
                # 公司隔离
                if hasattr(goal, 'company') and goal.company:
                    users = users.filter(profile__company=goal.company)
                
                # 排除创建人
                users = users.exclude(id=goal.created_by_id)
                
                for user in users:
                    try:
                        # 创建待办事项
                        Todo.objects.create(
                            todo_type='goal_decomposition',
                            title=f'目标分解：{goal.name}',
                            description=f'公司目标《{goal.name}》已发布，请创建个人目标进行对齐。',
                            assignee=user,
                            related_goal=goal,
                            deadline=deadline,
                            status='pending'
                        )
                        
                        # 发送通知
                        safe_approval_notification(
                            user=user,
                            title='[目标发布] 请创建个人目标',
                            content=f'公司目标《{goal.name}》已发布，请创建个人目标进行对齐。',
                            object_type='goal',
                            object_id=str(goal.id),
                            event='company_goal_published',
                            is_read=False
                        )
                    except Exception as e:
                        logger.error(f"为用户 {user.username} 创建目标分解待办失败：{str(e)}", exc_info=True)
            
            elif goal.level == 'personal' and goal.owner:
                # 个人目标：通知目标所有者
                try:
                    safe_approval_notification(
                        user=goal.owner,
                        title='[目标分配] 您有一个待接收的目标',
                        content=f'您有一个待接收的目标《{goal.name}》，请及时接收。',
                        object_type='goal',
                        object_id=str(goal.id),
                        event='personal_goal_published',
                        is_read=False
                    )
                except Exception as e:
                    logger.error(f"通知目标所有者失败：{str(e)}", exc_info=True)
    
    except Exception as e:
        logger.error(f"处理目标发布失败：{str(e)}", exc_info=True)


def handle_plan_published(plan):
    """
    处理计划发布后的动作
    
    当计划状态变为published时：
    - 如果是公司计划，通知所有员工并创建个人计划创建待办
    - 如果是个人计划，通知计划所有者
    """
    try:
        if plan.status == 'published' and plan.published_at:
            # 检查是否已有相关的待办事项（避免重复创建）
            existing_todos = Todo.objects.filter(
                related_plan=instance,
                todo_type='personal_plan_creation'
            ).exists()
            
            if existing_todos:
                return  # 已存在待办，跳过
            
            # 计算截止时间：当月27日 17:00
            now = timezone.now()
            current_month = now.month
            current_year = now.year
            
            deadline = timezone.make_aware(
                datetime(current_year, current_month, 27, 17, 0, 0)
            )
            
            if plan.level == 'company':
                # 公司计划：通知所有员工并创建个人计划创建待办
                users = User.objects.filter(is_active=True)
                
                # 公司隔离
                if hasattr(plan, 'company') and plan.company:
                    users = users.filter(profile__company=plan.company)
                
                # 排除创建人
                users = users.exclude(id=plan.created_by_id)
                
                for user in users:
                    try:
                        # 创建待办事项
                        Todo.objects.create(
                            todo_type='personal_plan_creation',
                            title=f'个人计划创建：{plan.name}',
                            description=f'公司计划《{plan.name}》已发布，请创建个人计划进行对齐。',
                            assignee=user,
                            related_plan=plan,
                            deadline=deadline,
                            status='pending'
                        )
                        
                        # 发送通知
                        safe_approval_notification(
                            user=user,
                            title='[计划发布] 请创建个人计划',
                            content=f'公司计划《{plan.name}》已发布，请创建个人计划进行对齐。',
                            object_type='plan',
                            object_id=str(plan.id),
                            event='company_plan_published',
                            is_read=False
                        )
                    except Exception as e:
                        logger.error(f"为用户 {user.username} 创建个人计划创建待办失败：{str(e)}", exc_info=True)
            
            elif plan.level == 'personal' and plan.owner:
                # 个人计划：通知计划所有者
                try:
                    safe_approval_notification(
                        user=plan.owner,
                        title='[计划分配] 您有一个待接收的计划',
                        content=f'您有一个待接收的计划《{plan.name}》，请及时接收。',
                        object_type='plan',
                        object_id=str(plan.id),
                        event='personal_plan_published',
                        is_read=False
                    )
                except Exception as e:
                    logger.error(f"通知计划所有者失败：{str(e)}", exc_info=True)
    
    except Exception as e:
        logger.error(f"处理计划发布失败：{str(e)}", exc_info=True)


@receiver(post_save, sender=GoalProgressRecord)
def handle_goal_progress_update(sender, instance, created, **kwargs):
    """
    监听目标进度更新
    
    当目标进度更新后，通知其上级查阅
    """
    if not created:
        return  # 只处理新建的进度记录
    
    try:
        goal = instance.goal
        
        # 通知上级（responsible_person，如果与记录人不同）
        if goal.responsible_person and goal.responsible_person != instance.recorded_by:
            safe_approval_notification(
                user=goal.responsible_person,
                title='[目标进度] 目标进度已更新',
                content=f'{instance.recorded_by.get_full_name() or instance.recorded_by.username} 更新了目标《{goal.name}》的进度，当前完成率：{instance.completion_rate}%。',
                object_type='goal',
                object_id=str(goal.id),
                event='goal_progress_updated',
                is_read=False
            )
    except Exception as e:
        logger.error(f"通知目标进度更新失败：{str(e)}", exc_info=True)


@receiver(post_save, sender=PlanProgressRecord)
def handle_plan_progress_update(sender, instance, created, **kwargs):
    """
    监听计划进度更新
    
    当计划进度更新后，通知其上级查阅
    """
    if not created:
        return  # 只处理新建的进度记录
    
    try:
        plan = instance.plan
        
        # 通知上级（responsible_person，如果与记录人不同）
        if plan.responsible_person and plan.responsible_person != instance.recorded_by:
            safe_approval_notification(
                user=plan.responsible_person,
                title='[计划进度] 计划进度已更新',
                content=f'{instance.recorded_by.get_full_name() or instance.recorded_by.username} 更新了计划《{plan.name}》的进度，当前进度：{instance.progress}%。',
                object_type='plan',
                object_id=str(plan.id),
                event='plan_progress_updated',
                is_read=False
            )
    except Exception as e:
        logger.error(f"通知计划进度更新失败：{str(e)}", exc_info=True)
