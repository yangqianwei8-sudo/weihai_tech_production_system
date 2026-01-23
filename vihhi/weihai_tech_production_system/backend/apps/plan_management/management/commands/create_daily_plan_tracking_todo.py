"""
计划跟踪待办任务

系统每天下午5点，系统自动通知员工，更新计划进度，截止时间为下午6点。

使用方式：
- 通过cron或celery beat调用：python manage.py create_daily_plan_tracking_todo
- 建议cron配置：0 17 * * * python manage.py create_daily_plan_tracking_todo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from backend.apps.plan_management.models import Todo, Plan
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '计划跟踪待办 - 每天17点生成计划进度更新待办，截止当天18点'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不创建待办和通知',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('计划跟踪待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不创建待办'))
        
        now = timezone.now()
        today = now.date()
        
        # 计算截止时间：今天 18:00
        deadline = timezone.make_aware(
            datetime.combine(today, datetime.min.time().replace(hour=18, minute=0))
        )
        
        # 查找所有有进行中计划的员工
        active_plans = Plan.objects.filter(
            level='personal',
            status__in=['accepted', 'in_progress'],
            owner__isnull=False
        ).select_related('owner')
        
        # 按员工分组
        user_plans = {}
        for plan in active_plans:
            if plan.owner not in user_plans:
                user_plans[plan.owner] = []
            user_plans[plan.owner].append(plan)
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for user, plans in user_plans.items():
            try:
                # 检查是否已存在今天的待办
                today_start = timezone.make_aware(
                    datetime.combine(today, datetime.min.time())
                )
                existing_todo = Todo.objects.filter(
                    assignee=user,
                    todo_type='plan_progress_update',
                    deadline__gte=today_start,
                    deadline__lte=deadline
                ).first()
                
                if existing_todo:
                    skipped_count += 1
                    continue
                
                if not dry_run:
                    # 创建待办事项
                    plan_names = [p.name for p in plans[:3]]  # 最多显示3个
                    if len(plans) > 3:
                        plan_names.append(f'等{len(plans)}个计划')
                    
                    todo = Todo.objects.create(
                        todo_type='plan_progress_update',
                        title='计划进度更新',
                        description=f'请更新以下计划的进度：{", ".join(plan_names)}',
                        assignee=user,
                        deadline=deadline,
                        status='pending'
                    )
                    
                    # 发送通知
                    safe_approval_notification(
                        user=user,
                        title='[计划跟踪] 请更新计划进度',
                        content=f'系统已为您创建计划进度更新待办事项，请在{deadline.strftime("%H:%M")}前完成。',
                        object_type='todo',
                        object_id=str(todo.id),
                        event='plan_progress_update',
                        is_read=False
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {user.username}: {len(plans)} 个计划'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {user.username}: {len(plans)} 个计划'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"为用户 {user.username} 创建计划跟踪待办失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'跳过（已有待办）：{skipped_count} 个用户'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
