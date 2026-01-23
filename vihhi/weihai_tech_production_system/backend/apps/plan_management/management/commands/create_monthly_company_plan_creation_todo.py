"""
月度公司计划创建待办任务

每月20日上午10点，系统自动生成一条月度公司计划创建的待办事项，并通知总经理。截止时间为每月23日下午5点。

使用方式：
- 通过cron或celery beat调用：python manage.py create_monthly_company_plan_creation_todo
- 建议cron配置：0 10 20 * * python manage.py create_monthly_company_plan_creation_todo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from backend.apps.plan_management.models import Todo
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '月度公司计划创建待办 - 每月20日10点生成公司计划创建待办，通知总经理，截止23日17点'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不创建待办和通知',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('月度公司计划创建待办任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不创建待办'))
        
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # 计算截止时间：当月23日 17:00
        deadline = timezone.make_aware(
            datetime(current_year, current_month, 23, 17, 0, 0)
        )
        
        # 查找总经理
        from django.contrib.auth.models import Permission
        try:
            perm = Permission.objects.get(
                codename='approve_plan',
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
                # 检查是否已存在本月的待办
                month_start = timezone.make_aware(
                    datetime(current_year, current_month, 1, 0, 0, 0)
                )
                existing_todo = Todo.objects.filter(
                    assignee=gm,
                    todo_type='company_plan_creation',
                    deadline__gte=month_start,
                    deadline__lte=deadline
                ).first()
                
                if existing_todo:
                    self.stdout.write(self.style.WARNING(f'  {gm.username} 已有本月公司计划创建待办，跳过'))
                    continue
                
                if not dry_run:
                    # 创建待办事项
                    todo = Todo.objects.create(
                        todo_type='company_plan_creation',
                        title=f'{current_year}年{current_month}月公司计划创建',
                        description=f'请创建{current_year}年{current_month}月的公司计划，截止时间：{deadline.strftime("%Y-%m-%d %H:%M")}',
                        assignee=gm,
                        deadline=deadline,
                        status='pending'
                    )
                    
                    # 发送通知
                    safe_approval_notification(
                        user=gm,
                        title='[月度计划] 请创建公司计划',
                        content=f'系统已为您创建月度公司计划创建待办事项，请在{deadline.strftime("%Y-%m-%d %H:%M")}前完成。',
                        object_type='todo',
                        object_id=str(todo.id),
                        event='company_plan_creation',
                        is_read=False
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {gm.username}: 已创建待办'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {gm.username}: 将创建待办'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"为总经理 {gm.username} 创建公司计划创建待办失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {gm.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
