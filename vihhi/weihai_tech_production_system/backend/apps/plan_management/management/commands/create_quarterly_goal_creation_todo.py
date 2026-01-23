"""
季度目标创建待办任务

每个自然季度起始月的1日9点，系统自动生成一条目标创建的待办事项，并通知总经理，截止时间为10日9点。

使用方式：
- 通过cron或celery beat调用：python manage.py create_quarterly_goal_creation_todo
- 建议cron配置：0 9 1 1,4,7,10 * python manage.py create_quarterly_goal_creation_todo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from backend.apps.plan_management.models import Todo
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '季度目标创建待办 - 每季度1日9点生成目标创建待办，通知总经理'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不创建待办和通知',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('季度目标创建待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不创建待办'))
        
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # 判断是否为季度起始月（1月、4月、7月、10月）
        if current_month not in [1, 4, 7, 10]:
            self.stdout.write(self.style.WARNING(f'当前月份 {current_month} 不是季度起始月，跳过'))
            return
        
        # 计算截止时间：当月10日 09:00
        deadline = timezone.make_aware(
            datetime(current_year, current_month, 10, 9, 0, 0)
        )
        
        # 查找总经理（通过角色或权限识别）
        # 简化实现：查找拥有 plan_management.approve_strategicgoal 权限的用户
        from django.contrib.auth.models import Permission
        try:
            perm = Permission.objects.get(
                codename='approve_strategicgoal',
                content_type__app_label='plan_management'
            )
            general_managers = User.objects.filter(
                Q(user_permissions=perm) | Q(groups__permissions=perm)
            ).filter(is_active=True).distinct()
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR('未找到审批权限，无法识别总经理'))
            return
        
        if not general_managers.exists():
            self.stdout.write(self.style.WARNING('未找到总经理用户'))
            return
        
        success_count = 0
        error_count = 0
        
        for gm in general_managers:
            try:
                # 检查是否已存在本季度的待办
                quarter_start = timezone.make_aware(
                    datetime(current_year, current_month, 1, 0, 0, 0)
                )
                existing_todo = Todo.objects.filter(
                    assignee=gm,
                    todo_type='goal_creation',
                    deadline__gte=quarter_start,
                    deadline__lte=deadline
                ).first()
                
                if existing_todo:
                    self.stdout.write(self.style.WARNING(f'  {gm.username} 已有本季度目标创建待办，跳过'))
                    continue
                
                if not dry_run:
                    # 创建待办事项
                    todo = Todo.objects.create(
                        todo_type='goal_creation',
                        title=f'{current_year}年第{((current_month-1)//3)+1}季度目标创建',
                        description=f'请创建{current_year}年第{((current_month-1)//3)+1}季度的公司目标，截止时间：{deadline.strftime("%Y-%m-%d %H:%M")}',
                        assignee=gm,
                        deadline=deadline,
                        status='pending'
                    )
                    
                    # 发送通知
                    safe_approval_notification(
                        user=gm,
                        title='[季度目标] 请创建季度目标',
                        content=f'系统已为您创建季度目标创建待办事项，请在{deadline.strftime("%Y-%m-%d %H:%M")}前完成。',
                        object_type='todo',
                        object_id=str(todo.id),
                        event='goal_creation',
                        is_read=False
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {gm.username}: 已创建待办'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {gm.username}: 将创建待办'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"为总经理 {gm.username} 创建目标创建待办失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {gm.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
