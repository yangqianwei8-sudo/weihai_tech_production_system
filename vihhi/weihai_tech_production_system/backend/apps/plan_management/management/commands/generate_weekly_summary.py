"""
生成周报任务

每周一上午9点：系统自动汇总员工上周目标更新进度、周计划任务完成情况，生成每周简报，一键发送给员工及其上级。

使用方式：
- 通过cron或celery beat调用：python manage.py generate_weekly_summary
- 建议cron配置：0 9 * * 1 python manage.py generate_weekly_summary
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.apps.plan_management.services.summary_service import send_weekly_summary_to_user
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '生成周报 - 每周一9点生成并发送上周工作总结'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不发送报告',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='指定用户（测试用）',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        username = options.get('user')
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('生成周报任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不发送报告'))
        
        # 获取用户列表
        if username:
            users = User.objects.filter(username=username, is_active=True)
        else:
            users = User.objects.filter(is_active=True)
        
        total_users = users.count()
        self.stdout.write(f'\n处理用户数：{total_users}')
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                if not dry_run:
                    result = send_weekly_summary_to_user(user)
                    if result:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ {user.username}'))
                        success_count += 1
                    else:
                        self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: 发送失败'))
                        error_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  [DRY RUN] {user.username}'))
                    success_count += 1
                
            except Exception as e:
                logger.error(f"处理用户 {user.username} 的周报失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
