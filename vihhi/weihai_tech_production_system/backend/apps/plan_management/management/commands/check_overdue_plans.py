"""
检查逾期计划任务

若任务在截止日未完成，自动延期并标记为"逾期"，同时自动通知员工及其上级。

使用方式：
- 通过cron或celery beat调用：python manage.py check_overdue_plans
- 建议cron配置：0 9 * * * python manage.py check_overdue_plans
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.apps.plan_management.models import Plan, StrategicGoal
from backend.apps.plan_management.notifications import safe_approval_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '检查逾期计划 - 每天9点检查并标记逾期计划，通知相关人员'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不实际标记逾期',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('检查逾期计划任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不标记逾期'))
        
        now = timezone.now()
        today = now.date()
        
        # 查找逾期计划（状态为in_progress且end_time已过）
        overdue_plans = Plan.objects.filter(
            status='in_progress',
            end_time__lt=now,
            is_overdue=False  # 只处理未标记为逾期的
        ).select_related('owner', 'responsible_person', 'responsible_department')
        
        plan_count = 0
        error_count = 0
        
        for plan in overdue_plans:
            try:
                if not dry_run:
                    # 标记为逾期
                    plan.is_overdue = True
                    plan.save()
                    
                    # 通知员工
                    if plan.owner:
                        safe_approval_notification(
                            user=plan.owner,
                            title='[计划逾期] 计划已逾期',
                            content=f'您的计划《{plan.name}》已超过截止时间，系统已自动标记为逾期，请尽快处理。',
                            object_type='plan',
                            object_id=str(plan.id),
                            event='plan_overdue',
                            is_read=False
                        )
                    
                    # 通知上级（如果有responsible_department，通知部门负责人）
                    # 简化实现：通知responsible_person（如果与owner不同）
                    if plan.responsible_person and plan.owner and plan.responsible_person != plan.owner:
                        safe_approval_notification(
                            user=plan.responsible_person,
                            title='[下属计划逾期] 下属计划已逾期',
                            content=f'您负责的计划《{plan.name}》（负责人：{plan.owner.get_full_name() or plan.owner.username}）已逾期，请跟进。',
                            object_type='plan',
                            object_id=str(plan.id),
                            event='subordinate_plan_overdue',
                            is_read=False
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {plan.plan_number}: {plan.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {plan.plan_number}: {plan.name}'))
                
                plan_count += 1
                
            except Exception as e:
                logger.error(f"标记逾期计划 {plan.plan_number} 失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {plan.plan_number}: {str(e)}'))
                error_count += 1
        
        # 检查逾期目标
        overdue_goals = StrategicGoal.objects.filter(
            status='in_progress',
            end_date__lt=today
        ).select_related('owner', 'responsible_person')
        
        goal_count = 0
        for goal in overdue_goals:
            try:
                if not dry_run:
                    # 通知员工
                    if goal.owner:
                        safe_approval_notification(
                            user=goal.owner,
                            title='[目标逾期] 目标已逾期',
                            content=f'您的目标《{goal.name}》已超过截止时间，请尽快处理。',
                            object_type='goal',
                            object_id=str(goal.id),
                            event='goal_overdue',
                            is_read=False
                        )
                    
                    # 通知上级
                    if goal.responsible_person and goal.owner and goal.responsible_person != goal.owner:
                        safe_approval_notification(
                            user=goal.responsible_person,
                            title='[下属目标逾期] 下属目标已逾期',
                            content=f'您负责的目标《{goal.name}》（负责人：{goal.owner.get_full_name() or goal.owner.username}）已逾期，请跟进。',
                            object_type='goal',
                            object_id=str(goal.id),
                            event='subordinate_goal_overdue',
                            is_read=False
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {goal.goal_number}: {goal.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {goal.goal_number}: {goal.name}'))
                
                goal_count += 1
                
            except Exception as e:
                logger.error(f"处理逾期目标 {goal.goal_number} 失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {goal.goal_number}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'计划：{plan_count} 个，目标：{goal_count} 个')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个'))
