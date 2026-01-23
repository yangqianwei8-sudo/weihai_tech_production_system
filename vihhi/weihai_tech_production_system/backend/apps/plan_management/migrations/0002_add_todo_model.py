# Generated manually for plan management adjustment

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('plan_management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('todo_type', models.CharField(choices=[
                    ('goal_creation', '目标创建'),
                    ('goal_decomposition', '目标分解'),
                    ('goal_progress_update', '目标进度更新'),
                    ('company_plan_creation', '公司计划创建'),
                    ('personal_plan_creation', '个人计划创建'),
                    ('weekly_plan_decomposition', '周计划分解'),
                    ('daily_plan_decomposition', '日计划分解'),
                    ('plan_progress_update', '计划进度更新'),
                ], max_length=50, verbose_name='待办类型')),
                ('title', models.CharField(max_length=200, verbose_name='待办标题')),
                ('description', models.TextField(blank=True, verbose_name='待办描述')),
                ('deadline', models.DateTimeField(verbose_name='截止时间')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('status', models.CharField(choices=[
                    ('pending', '待处理'),
                    ('in_progress', '进行中'),
                    ('completed', '已完成'),
                    ('overdue', '已逾期'),
                    ('cancelled', '已取消'),
                ], default='pending', max_length=20, verbose_name='状态')),
                ('is_overdue', models.BooleanField(db_index=True, default=False, verbose_name='是否逾期')),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_todos', to=settings.AUTH_USER_MODEL, verbose_name='负责人')),
                ('created_by', models.ForeignKey(blank=True, help_text='系统自动创建时可为空', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_todos', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('related_goal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='plan_management.strategicgoal', verbose_name='关联目标')),
                ('related_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='plan_management.plan', verbose_name='关联计划')),
            ],
            options={
                'verbose_name': '待办事项',
                'verbose_name_plural': '待办事项',
                'db_table': 'plan_todo',
                'ordering': ['-created_time'],
            },
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['assignee', 'status'], name='plan_todo_assignee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['deadline'], name='plan_todo_deadline_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['is_overdue', 'status'], name='plan_todo_overdue_status_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['todo_type', 'status'], name='plan_todo_type_status_idx'),
        ),
    ]
