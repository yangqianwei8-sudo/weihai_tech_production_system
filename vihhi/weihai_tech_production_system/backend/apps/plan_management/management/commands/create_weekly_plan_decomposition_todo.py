"""
周计划分解待办任务

每周五上午9点，系统为每位员工生成一条计划分解（周计划）的待办事项，并通知员工。截止时间为每周五下午六点。

使用方式：
- 通过cron或celery beat调用：python manage.py create_weekly_plan_decomposition_todo
- 建议cron配置：0 9 * * 5 python manage.py create_weekly_plan_decomposition_todo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from backend.apps.plan_management.models import Todo
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '周计划分解待办 - 每周五9点生成周计划分解待办，截止当天18点'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不创建待办和通知',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('周计划分解待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不创建待办'))
        
        now = timezone.now()
        today = now.date()
        
        # 计算截止时间：今天 18:00
        deadline = timezone.make_aware(
            datetime.combine(today, datetime.min.time().replace(hour=18, minute=0))
        )
        
        # 获取所有活跃员工
        users = User.objects.filter(is_active=True)
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for user in users:
            try:
                # 检查是否已存在本周的待办
                week_start = today - timedelta(days=today.weekday())
                week_start_datetime = timezone.make_aware(
                    datetime.combine(week_start, datetime.min.time())
                )
                existing_todo = Todo.objects.filter(
                    assignee=user,
                    todo_type='weekly_plan_decomposition',
                    deadline__gte=week_start_datetime,
                    deadline__lte=deadline
                ).first()
                
                if existing_todo:
                    skipped_count += 1
                    continue
                
                if not dry_run:
                    # 创建待办事项
                    todo = Todo.objects.create(
                        todo_type='weekly_plan_decomposition',
                        title='周计划分解',
                        description='请创建本周的周计划，截止时间：今天18:00',
                        assignee=user,
                        deadline=deadline,
                        status='pending'
                    )
                    
                    # 发送通知
                    safe_approval_notification(
                        user=user,
                        title='[周计划] 请创建周计划',
                        content=f'系统已为您创建周计划分解待办事项，请在{deadline.strftime("%H:%M")}前完成。',
                        object_type='todo',
                        object_id=str(todo.id),
                        event='weekly_plan_decomposition',
                        is_read=False
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {user.username}'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"为用户 {user.username} 创建周计划分解待办失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'跳过（已有待办）：{skipped_count} 个用户'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
