# 计划管理流程调整实施总结

## 实施完成情况

✅ 所有功能已实现完成！

## 一、已实现的功能

### 1. 数据模型
- ✅ **Todo模型**：支持8种待办类型
  - 目标创建、目标分解、目标进度更新
  - 公司计划创建、个人计划创建
  - 周计划分解、日计划分解、计划进度更新

### 2. 目标管理系统动作
- ✅ **季度目标创建待办**：每季度1日9点自动生成，通知总经理，截止10日9点
- ✅ **目标分解待办**：目标发布后自动为员工创建，截止季度起始月10日9点
- ✅ **目标跟踪待办**：每周一10点生成，截止当天17点，更新后通知上级

### 3. 计划管理系统动作
- ✅ **月度公司计划创建待办**：每月20日10点生成，通知总经理，截止23日17点
- ✅ **个人计划创建待办**：公司计划发布后自动为员工创建，截止27日17点
- ✅ **周计划分解待办**：每周五9点生成，截止当天18点
- ✅ **日计划分解待办**：每天17点生成，截止次日18点
- ✅ **计划跟踪待办**：每天17点生成，截止当天18点，更新后通知上级

### 4. 计划状态自动流转
- ✅ **自动启动**：计划开始时间到达时自动变更为执行中
- ✅ **自动逾期标记**：截止日未完成自动标记逾期并通知相关人员
- ✅ **状态流转**：草稿→已确认→执行中→已完成/逾期

### 5. 工作总结功能
- ✅ **周报生成**：每周一9点自动生成并发送上周工作总结
- ✅ **月报生成**：每月1日9点自动生成并发送上月工作总结

### 6. 每日通知功能
- ✅ **昨日战报**：列出昨天已完成的任务和提前完成表扬
- ✅ **今日战场**：列出今日待办任务，高亮逾期任务
- ✅ **风险预警**：
  - 目标进度滞后提醒
  - 即将到期任务提醒
  - 下属逾期任务提醒

## 二、定时任务配置

### 建议的Cron配置

```bash
# 季度目标创建待办（每季度1日9点）
0 9 1 1,4,7,10 * python manage.py create_quarterly_goal_creation_todo

# 周目标跟踪待办（每周一10点）
0 10 * * 1 python manage.py create_weekly_goal_tracking_todo

# 月度公司计划创建待办（每月20日10点）
0 10 20 * * python manage.py create_monthly_company_plan_creation_todo

# 周计划分解待办（每周五9点）
0 9 * * 5 python manage.py create_weekly_plan_decomposition_todo

# 日计划分解待办（每天17点）
0 17 * * * python manage.py create_daily_plan_decomposition_todo

# 计划跟踪待办（每天17点）
0 17 * * * python manage.py create_daily_plan_tracking_todo

# 自动启动计划（每天9点）
0 9 * * * python manage.py auto_start_plans

# 检查逾期计划（每天9点）
0 9 * * * python manage.py check_overdue_plans

# 生成周报（每周一9点）
0 9 * * 1 python manage.py generate_weekly_summary

# 生成月报（每月1日9点）
0 9 1 * * python manage.py generate_monthly_summary

# 发送每日通知（每天9点）
0 9 * * * python manage.py send_daily_notification
```

### 使用Celery Beat（推荐）

如果项目使用Celery，可以在`celery.py`中配置：

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'quarterly-goal-creation': {
        'task': 'plan_management.management.commands.create_quarterly_goal_creation_todo',
        'schedule': crontab(hour=9, minute=0, day_of_month=1, month_of_year='1,4,7,10'),
    },
    'weekly-goal-tracking': {
        'task': 'plan_management.management.commands.create_weekly_goal_tracking_todo',
        'schedule': crontab(hour=10, minute=0, day_of_week=1),
    },
    # ... 其他任务
}
```

## 三、数据库迁移

需要运行数据库迁移：

```bash
python manage.py migrate plan_management
```

这将创建`plan_todo`表。

## 四、测试命令

所有命令都支持`--dry-run`参数进行测试：

```bash
# 测试季度目标创建待办
python manage.py create_quarterly_goal_creation_todo --dry-run

# 测试周报生成
python manage.py generate_weekly_summary --dry-run --user=testuser

# 测试每日通知
python manage.py send_daily_notification --dry-run --user=testuser
```

## 五、待办服务扩展

新增的待办查询功能：

```python
from backend.apps.plan_management.services.todo_service import (
    get_user_todos,           # 获取用户所有待办
    get_monthly_todos,         # 获取本月待办
    get_weekly_todos,          # 获取本周待办
    get_daily_todos,           # 获取今日待办
    get_user_todo_summary,     # 获取待办汇总统计
)
```

## 六、信号监听

系统已自动配置信号监听：

- **目标发布**：自动为员工创建目标分解待办
- **计划发布**：自动为员工创建个人计划创建待办
- **进度更新**：自动通知上级查阅

信号在`apps.py`中自动注册，无需手动配置。

## 七、注意事项

1. **总经理识别**：系统通过`approve_plan`和`approve_strategicgoal`权限识别总经理，确保相关用户拥有这些权限。

2. **公司隔离**：所有功能都支持公司数据隔离，通过`company`字段过滤。

3. **逾期检查**：系统每天自动检查并标记逾期任务，同时发送通知。

4. **通知系统**：所有通知通过`ApprovalNotification`模型存储，可通过通知中心查看。

## 八、后续优化建议

1. **上下级关系**：当前简化实现，后续可完善上下级关系查询逻辑
2. **项目阻塞检测**：当前简化实现，后续可关联项目管理系统实现更精确的阻塞检测
3. **报告格式**：当前为文本格式，后续可优化为HTML格式，支持更丰富的展示
4. **批量操作**：对于大量用户的场景，可考虑使用异步任务（Celery）处理

## 九、文件清单

### 新增文件
- `models.py` - 添加Todo模型
- `migrations/0002_add_todo_model.py` - Todo模型迁移
- `services/todo_service.py` - 扩展待办服务
- `services/summary_service.py` - 工作总结服务
- `services/daily_notification_service.py` - 每日通知服务
- `signals.py` - 信号监听
- `management/commands/create_quarterly_goal_creation_todo.py`
- `management/commands/create_weekly_goal_tracking_todo.py`
- `management/commands/create_monthly_company_plan_creation_todo.py`
- `management/commands/create_weekly_plan_decomposition_todo.py`
- `management/commands/create_daily_plan_decomposition_todo.py`
- `management/commands/create_daily_plan_tracking_todo.py`
- `management/commands/auto_start_plans.py`
- `management/commands/check_overdue_plans.py`
- `management/commands/generate_weekly_summary.py`
- `management/commands/generate_monthly_summary.py`
- `management/commands/send_daily_notification.py`

### 修改文件
- `models.py` - 在transition_to方法中添加状态变更处理
- `apps.py` - 注册信号监听
- `services/todo_service.py` - 扩展待办查询功能

## 十、完成状态

✅ 所有计划功能已实现完成，可以开始测试和部署！
