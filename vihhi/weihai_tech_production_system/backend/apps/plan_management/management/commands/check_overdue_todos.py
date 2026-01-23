"""
检查逾期待办任务

每天检查所有待办事项的逾期状态，自动标记为逾期。

使用方式：
- 通过cron或celery beat调用：python manage.py check_overdue_todos
- 建议cron配置：0 9 * * * python manage.py check_overdue_todos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.apps.plan_management.models import Todo
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '检查逾期待办 - 每天检查并标记逾期待办事项'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不实际标记逾期',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('检查逾期待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不标记逾期'))
        
        now = timezone.now()
        
        # 查找所有未完成且已过期的待办事项
        overdue_todos = Todo.objects.filter(
            status__in=['pending', 'in_progress'],
            deadline__lt=now,
            is_overdue=False  # 只处理未标记为逾期的
        ).select_related('assignee', 'related_goal', 'related_plan')
        
        todo_count = 0
        error_count = 0
        notified_count = 0
        
        for todo in overdue_todos:
            try:
                if not dry_run:
                    # 标记为逾期
                    todo.is_overdue = True
                    todo.status = 'overdue'
                    todo.save()
                    
                    # 通知负责人
                    try:
                        safe_approval_notification(
                            user=todo.assignee,
                            title='[待办逾期] 待办事项已逾期',
                            content=f'您的待办事项《{todo.title}》已超过截止时间（{todo.deadline.strftime("%Y-%m-%d %H:%M")}），请尽快处理。',
                            object_type='todo',
                            object_id=str(todo.id),
                            event='todo_overdue',
                            is_read=False
                        )
                        notified_count += 1
                    except Exception as e:
                        logger.warning(f"通知待办负责人失败：{str(e)}")
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {todo.id}: {todo.title} - {todo.assignee.username}'))
                else:
                    days_overdue = (now - todo.deadline).days
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {todo.id}: {todo.title} - {todo.assignee.username} (逾期{days_overdue}天)'))
                
                todo_count += 1
                
            except Exception as e:
                logger.error(f"标记逾期待办 {todo.id} 失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {todo.id}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'标记逾期：{todo_count} 个待办')
        if not dry_run:
            self.stdout.write(f'发送通知：{notified_count} 个用户')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个'))
