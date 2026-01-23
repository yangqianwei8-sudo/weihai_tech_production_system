"""
周目标跟踪待办任务

每周一上午10点，系统自动生成一条目标进度更新待办事项，并提醒员工，截止时间为下午五点。

使用方式：
- 通过cron或celery beat调用：python manage.py create_weekly_goal_tracking_todo
- 建议cron配置：0 10 * * 1 python manage.py create_weekly_goal_tracking_todo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from backend.apps.plan_management.models import Todo, StrategicGoal
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '周目标跟踪待办 - 每周一10点生成目标进度更新待办，截止当天17点'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不创建待办和通知',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('周目标跟踪待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不创建待办'))
        
        now = timezone.now()
        today = now.date()
        
        # 计算截止时间：今天 17:00
        deadline = timezone.make_aware(
            datetime.combine(today, datetime.min.time().replace(hour=17, minute=0))
        )
        
        # 查找所有有进行中目标的员工
        active_goals = StrategicGoal.objects.filter(
            level='personal',
            status__in=['accepted', 'in_progress'],
            owner__isnull=False
        ).select_related('owner')
        
        # 按员工分组
        user_goals = {}
        for goal in active_goals:
            if goal.owner not in user_goals:
                user_goals[goal.owner] = []
            user_goals[goal.owner].append(goal)
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for user, goals in user_goals.items():
            try:
                # 检查是否已存在本周的待办
                week_start = today - timedelta(days=today.weekday())
                week_start_datetime = timezone.make_aware(
                    datetime.combine(week_start, datetime.min.time())
                )
                existing_todo = Todo.objects.filter(
                    assignee=user,
                    todo_type='goal_progress_update',
                    deadline__gte=week_start_datetime,
                    deadline__lte=deadline
                ).first()
                
                if existing_todo:
                    skipped_count += 1
                    continue
                
                if not dry_run:
                    # 创建待办事项
                    goal_names = [g.name for g in goals[:3]]  # 最多显示3个
                    if len(goals) > 3:
                        goal_names.append(f'等{len(goals)}个目标')
                    
                    todo = Todo.objects.create(
                        todo_type='goal_progress_update',
                        title='目标进度更新',
                        description=f'请更新以下目标的进度：{", ".join(goal_names)}',
                        assignee=user,
                        deadline=deadline,
                        status='pending'
                    )
                    
                    # 发送通知
                    safe_approval_notification(
                        user=user,
                        title='[目标跟踪] 请更新目标进度',
                        content=f'系统已为您创建目标进度更新待办事项，请在{deadline.strftime("%H:%M")}前完成。',
                        object_type='todo',
                        object_id=str(todo.id),
                        event='goal_progress_update',
                        is_read=False
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {user.username}: {len(goals)} 个目标'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {user.username}: {len(goals)} 个目标'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"为用户 {user.username} 创建目标跟踪待办失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'跳过（已有待办）：{skipped_count} 个用户'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
