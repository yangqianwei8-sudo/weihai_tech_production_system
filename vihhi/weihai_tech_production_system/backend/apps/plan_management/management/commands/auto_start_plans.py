"""
自动启动计划任务

若系统时间到达任务的"计划开始日期"的上午9点时，若任务仍处于"已确认"状态，则自动变更为"执行中"。

使用方式：
- 通过cron或celery beat调用：python manage.py auto_start_plans
- 建议cron配置：0 9 * * * python manage.py auto_start_plans
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from backend.apps.plan_management.models import Plan
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '自动启动计划 - 每天9点检查并启动已到开始时间的计划'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不实际变更状态',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('自动启动计划任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不变更状态'))
        
        now = timezone.now()
        today_9am = timezone.make_aware(
            datetime.combine(now.date(), datetime.min.time().replace(hour=9, minute=0))
        )
        
        # 查找状态为accepted且开始时间已到的计划
        plans_to_start = Plan.objects.filter(
            status='accepted',
            start_time__lte=today_9am
        ).select_related('owner', 'responsible_person')
        
        success_count = 0
        error_count = 0
        
        for plan in plans_to_start:
            try:
                if not dry_run:
                    # 自动变更为执行中
                    plan.transition_to('in_progress')
                    
                    # 通知负责人
                    if plan.owner:
                        safe_approval_notification(
                            user=plan.owner,
                            title='[计划启动] 计划已自动启动',
                            content=f'您的计划《{plan.name}》已到达开始时间，系统已自动将其状态变更为"执行中"。',
                            object_type='plan',
                            object_id=str(plan.id),
                            event='plan_auto_started',
                            is_read=False
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {plan.plan_number}: {plan.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {plan.plan_number}: {plan.name}'))
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"自动启动计划 {plan.plan_number} 失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {plan.plan_number}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个计划')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个计划'))
