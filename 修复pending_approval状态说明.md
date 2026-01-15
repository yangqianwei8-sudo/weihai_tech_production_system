# 修复 pending_approval 状态数据不一致问题

## 问题描述

目标 `GOAL-20260108-0004` 的状态显示为 `pending_approval`，但这个状态不在 `StrategicGoal` 模型定义的有效状态选项中。

## 问题原因

1. **迁移历史**：迁移文件 `0010_add_pending_approval_to_goal.py` 曾经添加了 `pending_approval` 状态到 `StrategicGoal`
2. **模型变更**：但当前的模型定义 (`models.py`) 中，`STATUS_CHOICES` 不包含 `pending_approval` 状态
3. **数据不一致**：数据库中仍然有使用 `pending_approval` 状态的目标数据

## 当前模型定义的有效状态

```python
STATUS_CHOICES = [
    ('draft', '制定中'),
    ('published', '已发布'),
    ('in_progress', '执行中'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
]
```

## 解决方案

### 方案1：创建数据迁移（推荐）

已创建迁移文件：`0018_fix_pending_approval_status.py`

**执行迁移**：
```bash
cd /home/devbox/project/vihhi/weihai_tech_production_system
python manage.py migrate plan_management
```

**迁移内容**：
- 将所有状态为 `pending_approval` 的目标改为 `draft`（制定中）
- 这是合理的，因为 `pending_approval` 通常表示目标正在等待审批，可以归类为"制定中"

### 方案2：直接使用SQL修复

如果无法执行迁移，可以直接使用SQL：

```sql
-- 查看需要修复的目标
SELECT goal_number, name, status 
FROM plan_strategic_goal 
WHERE status = 'pending_approval';

-- 修复数据
UPDATE plan_strategic_goal 
SET status = 'draft' 
WHERE status = 'pending_approval';

-- 验证修复结果
SELECT status, COUNT(*) 
FROM plan_strategic_goal 
GROUP BY status 
ORDER BY status;
```

## 修复后的效果

- ✅ 所有目标的状态都在模型定义的有效状态范围内
- ✅ 页面显示正常，不会出现未定义的状态
- ✅ 统计卡片能正确统计所有状态的数据

## 注意事项

1. **数据备份**：在执行修复前，建议备份数据库
2. **状态映射**：`pending_approval` → `draft` 是合理的映射，因为两者都表示目标尚未正式发布
3. **后续处理**：如果业务需要审批流程，可以考虑：
   - 使用 `PlanDecision` 模型来处理审批（P1 已实现）
   - 或者重新添加 `pending_approval` 状态到模型中

## 相关文件

- **迁移文件**：`vihhi/weihai_tech_production_system/backend/apps/plan_management/migrations/0018_fix_pending_approval_status.py`
- **模型定义**：`vihhi/weihai_tech_production_system/backend/apps/plan_management/models.py` (第30-36行)
- **历史迁移**：`vihhi/weihai_tech_production_system/backend/apps/plan_management/migrations/0010_add_pending_approval_to_goal.py`

---

**创建日期**：2026-01-15  
**状态**：待执行迁移
