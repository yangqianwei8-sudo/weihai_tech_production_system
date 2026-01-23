# 数据库迁移执行指南

## 方法1：使用Django迁移（推荐）

在有Django环境的服务器上运行：

```bash
cd /workspace/vihhi/weihai_tech_production_system
python manage.py migrate plan_management
```

这将执行两个迁移：
- `0002_add_todo_model` - 创建Todo表
- `0003_extend_notification_event_types` - 扩展通知事件类型

## 方法2：使用SQL脚本（备选方案）

如果无法使用Django迁移，可以直接在数据库中执行SQL脚本：

### 步骤1：执行Todo表创建脚本

```bash
# 连接到PostgreSQL数据库
psql -U postgres -d weihai_tech -f backend/apps/plan_management/migrations/0002_add_todo_model.sql
```

或者直接在psql中执行：

```sql
\i backend/apps/plan_management/migrations/0002_add_todo_model.sql
```

### 步骤2：执行通知类型扩展脚本（可选）

```bash
psql -U postgres -d weihai_tech -f backend/apps/plan_management/migrations/0003_extend_notification_event_types.sql
```

### 步骤3：记录迁移状态（重要）

执行SQL后，需要手动在Django的迁移表中记录：

```sql
-- 记录0002迁移
INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0002_add_todo_model', NOW())
ON CONFLICT DO NOTHING;

-- 记录0003迁移
INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0003_extend_notification_event_types', NOW())
ON CONFLICT DO NOTHING;
```

## 方法3：使用Docker环境

如果项目使用Docker：

```bash
cd /workspace/vihhi/weihai_tech_production_system
docker-compose exec backend python manage.py migrate plan_management
```

## 验证迁移

迁移成功后，验证表是否创建：

```sql
-- 检查plan_todo表是否存在
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'plan_todo';

-- 查看表结构
\d plan_todo

-- 检查索引
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'plan_todo';
```

## 回滚迁移（如果需要）

### 使用Django迁移回滚

```bash
python manage.py migrate plan_management 0001_initial
```

### 使用SQL回滚

```sql
-- 删除表和相关对象
DROP TABLE IF EXISTS plan_todo CASCADE;

-- 删除迁移记录
DELETE FROM django_migrations 
WHERE app = 'plan_management' 
AND name IN ('0002_add_todo_model', '0003_extend_notification_event_types');
```

## 注意事项

1. **备份数据库**：执行迁移前请务必备份数据库
2. **测试环境**：建议先在测试环境验证
3. **权限检查**：确保数据库用户有CREATE TABLE和ALTER TABLE权限
4. **依赖检查**：确保`plan_strategic_goal`和`plan_plan`表已存在
5. **外键约束**：SQL脚本包含外键约束，确保相关表存在

## 常见问题

### Q: 迁移失败，提示表已存在
A: 表可能已手动创建，可以跳过或先删除表：
```sql
DROP TABLE IF EXISTS plan_todo CASCADE;
```

### Q: 外键约束失败
A: 检查相关表是否存在：
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('plan_strategic_goal', 'plan_plan', 'auth_user');
```

### Q: 索引创建失败
A: 索引可能已存在，使用`CREATE INDEX IF NOT EXISTS`可以避免错误
