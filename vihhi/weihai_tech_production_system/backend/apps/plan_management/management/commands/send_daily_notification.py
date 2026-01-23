"""
发送每日通知任务

每天上午9点推送：
1. 昨日战报：自动列出昨天已完成的工作任务，以及提前多天完成，对员工的出色表现给予肯定。
2. 今日战场：列出所有截止到今天，状态未完成的任务。高亮显示已逾期任务。
3. 风险预警：
   - "您有[X]个目标进度已滞后，点击查看。"
   - "您有[Y]个任务即将在三天内到期。"
   - "您负责的[项目A]关键路径任务已被阻塞[Z]天，需立即关注。"
   上级关注："您的下属[张三]有[3]项任务已逾期，请跟进。"

使用方式：
- 通过cron或celery beat调用：python manage.py send_daily_notification
- 建议cron配置：0 9 * * * python manage.py send_daily_notification
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.apps.plan_management.services.daily_notification_service import send_daily_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '发送每日通知 - 每天9点发送昨日战报、今日战场、风险预警'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示统计，不发送通知',
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
        self.stdout.write(self.style.SUCCESS('发送每日通知任务'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('【DRY RUN 模式】仅统计，不发送通知'))
        
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
                    result = send_daily_notification(user)
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
                logger.error(f"处理用户 {user.username} 的每日通知失败：{str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {str(e)}'))
                error_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('任务完成'))
        self.stdout.write(f'成功：{success_count} 个用户')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'失败：{error_count} 个用户'))
