# Generated manually to add overdue fields to Plan model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan_management', '0027_fix_plan_type_nullable'),
    ]

    operations = [
        # 添加风险预警字段（周计划专用）
        migrations.AddField(
            model_name='plan',
            name='is_overdue',
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name='是否逾期',
                help_text='周计划提交是否逾期'
            ),
        ),
        migrations.AddField(
            model_name='plan',
            name='overdue_days',
            field=models.IntegerField(
                default=0,
                verbose_name='逾期天数',
                help_text='周计划逾期天数'
            ),
        ),
        migrations.AddField(
            model_name='plan',
            name='risk_level',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('low', '低风险'),
                    ('medium', '中风险'),
                    ('high', '高风险'),
                    ('critical', '严重风险'),
                ],
                default='low',
                blank=True,
                verbose_name='风险等级',
                help_text='周计划逾期风险等级'
            ),
        ),
        migrations.AddField(
            model_name='plan',
            name='submission_deadline',
            field=models.DateTimeField(
                null=True,
                blank=True,
                verbose_name='提交截止时间',
                help_text='周计划提交截止时间（每周五18:00）'
            ),
        ),
        # 添加索引
        migrations.AddIndex(
            model_name='plan',
            index=models.Index(fields=['is_overdue', 'risk_level'], name='plan_plan_is_overdue_risk_idx'),
        ),
        migrations.AddIndex(
            model_name='plan',
            index=models.Index(fields=['plan_period', 'is_overdue'], name='plan_plan_period_overdue_idx'),
        ),
    ]
