# 定时任务配置指南

## 所有定时任务列表

### 1. 季度目标创建待办
```bash
0 9 1 1,4,7,10 * cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_quarterly_goal_creation_todo
```
**说明**：每季度1日（1月、4月、7月、10月）9点执行

### 2. 周目标跟踪待办
```bash
0 10 * * 1 cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_weekly_goal_tracking_todo
```
**说明**：每周一10点执行

### 3. 月度公司计划创建待办
```bash
0 10 20 * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_monthly_company_plan_creation_todo
```
**说明**：每月20日10点执行

### 4. 周计划分解待办
```bash
0 9 * * 5 cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_weekly_plan_decomposition_todo
```
**说明**：每周五9点执行

### 5. 日计划分解待办
```bash
0 17 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_daily_plan_decomposition_todo
```
**说明**：每天17点执行

### 6. 计划跟踪待办
```bash
0 17 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py create_daily_plan_tracking_todo
```
**说明**：每天17点执行

### 7. 自动启动计划
```bash
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py auto_start_plans
```
**说明**：每天9点执行

### 8. 检查逾期计划
```bash
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py check_overdue_plans
```
**说明**：每天9点执行

### 9. 检查逾期待办
```bash
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py check_overdue_todos
```
**说明**：每天9点执行

### 10. 生成周报
```bash
0 9 * * 1 cd /workspace/vihhi/weihai_tech_production_system && python manage.py generate_weekly_summary
```
**说明**：每周一9点执行

### 11. 生成月报
```bash
0 9 1 * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py generate_monthly_summary
```
**说明**：每月1日9点执行

### 12. 发送每日通知
```bash
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && python manage.py send_daily_notification
```
**说明**：每天9点执行

## 完整Crontab配置

将以下内容添加到 `/etc/crontab` 或用户的 crontab（`crontab -e`）：

```bash
# 计划管理定时任务
# 季度目标创建待办（每季度1日9点）
0 9 1 1,4,7,10 * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_quarterly_goal_creation_todo >> /var/log/plan_management.log 2>&1

# 周目标跟踪待办（每周一10点）
0 10 * * 1 cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_weekly_goal_tracking_todo >> /var/log/plan_management.log 2>&1

# 月度公司计划创建待办（每月20日10点）
0 10 20 * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_monthly_company_plan_creation_todo >> /var/log/plan_management.log 2>&1

# 周计划分解待办（每周五9点）
0 9 * * 5 cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_weekly_plan_decomposition_todo >> /var/log/plan_management.log 2>&1

# 日计划分解待办（每天17点）
0 17 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_daily_plan_decomposition_todo >> /var/log/plan_management.log 2>&1

# 计划跟踪待办（每天17点）
0 17 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py create_daily_plan_tracking_todo >> /var/log/plan_management.log 2>&1

# 自动启动计划（每天9点）
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py auto_start_plans >> /var/log/plan_management.log 2>&1

# 检查逾期计划（每天9点）
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py check_overdue_plans >> /var/log/plan_management.log 2>&1

# 检查逾期待办（每天9点）
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py check_overdue_todos >> /var/log/plan_management.log 2>&1

# 生成周报（每周一9点）
0 9 * * 1 cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py generate_weekly_summary >> /var/log/plan_management.log 2>&1

# 生成月报（每月1日9点）
0 9 1 * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py generate_monthly_summary >> /var/log/plan_management.log 2>&1

# 发送每日通知（每天9点）
0 9 * * * cd /workspace/vihhi/weihai_tech_production_system && /usr/bin/python3 manage.py send_daily_notification >> /var/log/plan_management.log 2>&1
```

## 使用Celery Beat（推荐）

如果项目使用Celery，可以在`celery.py`中配置：

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'quarterly-goal-creation': {
        'task': 'plan_management.tasks.create_quarterly_goal_creation_todo',
        'schedule': crontab(hour=9, minute=0, day_of_month=1, month_of_year='1,4,7,10'),
    },
    'weekly-goal-tracking': {
        'task': 'plan_management.tasks.create_weekly_goal_tracking_todo',
        'schedule': crontab(hour=10, minute=0, day_of_week=1),
    },
    'monthly-company-plan-creation': {
        'task': 'plan_management.tasks.create_monthly_company_plan_creation_todo',
        'schedule': crontab(hour=10, minute=0, day_of_month=20),
    },
    'weekly-plan-decomposition': {
        'task': 'plan_management.tasks.create_weekly_plan_decomposition_todo',
        'schedule': crontab(hour=9, minute=0, day_of_week=5),
    },
    'daily-plan-decomposition': {
        'task': 'plan_management.tasks.create_daily_plan_decomposition_todo',
        'schedule': crontab(hour=17, minute=0),
    },
    'daily-plan-tracking': {
        'task': 'plan_management.tasks.create_daily_plan_tracking_todo',
        'schedule': crontab(hour=17, minute=0),
    },
    'auto-start-plans': {
        'task': 'plan_management.tasks.auto_start_plans',
        'schedule': crontab(hour=9, minute=0),
    },
    'check-overdue-plans': {
        'task': 'plan_management.tasks.check_overdue_plans',
        'schedule': crontab(hour=9, minute=0),
    },
    'check-overdue-todos': {
        'task': 'plan_management.tasks.check_overdue_todos',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-weekly-summary': {
        'task': 'plan_management.tasks.generate_weekly_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    'generate-monthly-summary': {
        'task': 'plan_management.tasks.generate_monthly_summary',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),
    },
    'send-daily-notification': {
        'task': 'plan_management.tasks.send_daily_notification',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

## 测试命令

所有命令都支持`--dry-run`参数进行测试：

```bash
# 测试季度目标创建待办
python manage.py create_quarterly_goal_creation_todo --dry-run

# 测试周报生成（指定用户）
python manage.py generate_weekly_summary --dry-run --user=testuser

# 测试每日通知（指定用户）
python manage.py send_daily_notification --dry-run --user=testuser
```

## 注意事项

1. **路径配置**：确保cron配置中的路径正确，使用绝对路径
2. **Python路径**：使用`which python3`查找Python的绝对路径
3. **日志记录**：建议将所有输出重定向到日志文件，便于排查问题
4. **权限检查**：确保运行cron的用户有执行命令的权限
5. **环境变量**：如果Django需要特定的环境变量，需要在cron中设置

## 验证定时任务

```bash
# 查看cron日志
tail -f /var/log/cron.log

# 查看应用日志
tail -f /var/log/plan_management.log

# 手动执行测试
python manage.py create_quarterly_goal_creation_todo --dry-run
```
