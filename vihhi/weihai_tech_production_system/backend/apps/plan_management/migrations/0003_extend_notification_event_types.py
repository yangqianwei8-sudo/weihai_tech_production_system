# Generated manually for extending notification event types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan_management', '0002_add_todo_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvalnotification',
            name='event',
            field=models.CharField(
                choices=[
                    ('submit', '提交审批'),
                    ('approve', '审批通过'),
                    ('reject', '审批驳回'),
                    ('cancel', '取消审批'),
                    ('draft_timeout', '草稿超时'),
                    ('approval_timeout', '审批超时'),
                    ('company_goal_published', '公司目标发布'),
                    ('personal_goal_published', '个人目标发布'),
                    ('goal_accepted', '目标被接收'),
                    ('company_plan_published', '公司计划发布'),
                    ('personal_plan_published', '个人计划发布'),
                    ('plan_accepted', '计划被接收'),
                    ('weekly_plan_reminder', '周计划提醒'),
                    ('weekly_plan_overdue', '周计划逾期'),
                    ('goal_creation', '目标创建待办'),
                    ('goal_decomposition', '目标分解待办'),
                    ('goal_progress_update', '目标进度更新待办'),
                    ('goal_progress_updated', '目标进度已更新'),
                    ('goal_overdue', '目标逾期'),
                    ('subordinate_goal_overdue', '下属目标逾期'),
                    ('company_plan_creation', '公司计划创建待办'),
                    ('personal_plan_creation', '个人计划创建待办'),
                    ('weekly_plan_decomposition', '周计划分解待办'),
                    ('daily_plan_decomposition', '日计划分解待办'),
                    ('plan_progress_update', '计划进度更新待办'),
                    ('plan_progress_updated', '计划进度已更新'),
                    ('plan_auto_started', '计划自动启动'),
                    ('plan_overdue', '计划逾期'),
                    ('subordinate_plan_overdue', '下属计划逾期'),
                    ('todo_overdue', '待办逾期'),
                    ('daily_todo_reminder', '每日待办提醒'),
                    ('weekly_summary', '周报'),
                    ('monthly_summary', '月报'),
                    ('daily_notification', '每日通知'),
                ],
                max_length=50,
                verbose_name='事件类型'
            ),
        ),
        migrations.AlterField(
            model_name='approvalnotification',
            name='object_type',
            field=models.CharField(
                choices=[
                    ('plan', '计划'),
                    ('goal', '目标'),
                    ('todo', '待办'),
                    ('summary', '总结'),
                    ('notification', '通知'),
                ],
                max_length=20,
                verbose_name='对象类型'
            ),
        ),
    ]
