# 快速迁移指南

## ✅ 迁移文件状态

所有迁移文件已验证通过！

- ✅ `0002_add_todo_model.py` - Django迁移文件
- ✅ `0002_add_todo_model.sql` - SQL脚本（可直接执行）
- ✅ `0003_extend_notification_event_types.py` - Django迁移文件
- ✅ `0003_extend_notification_event_types.sql` - SQL脚本（可直接执行）

## 🚀 快速执行迁移

### 方法1：Django迁移（推荐）

```bash
cd /workspace/vihhi/weihai_tech_production_system
python manage.py migrate plan_management
```

### 方法2：直接执行SQL（最快）

```bash
# 连接到数据库并执行SQL
psql -U postgres -d weihai_tech -f backend/apps/plan_management/migrations/0002_add_todo_model.sql
psql -U postgres -d weihai_tech -f backend/apps/plan_management/migrations/0003_extend_notification_event_types.sql

# 记录迁移状态（重要！）
psql -U postgres -d weihai_tech -c "
INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0002_add_todo_model', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0003_extend_notification_event_types', NOW())
ON CONFLICT DO NOTHING;
"
```

### 方法3：在psql中执行

```sql
-- 连接到数据库
\c weihai_tech

-- 执行迁移脚本
\i backend/apps/plan_management/migrations/0002_add_todo_model.sql
\i backend/apps/plan_management/migrations/0003_extend_notification_event_types.sql

-- 记录迁移状态
INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0002_add_todo_model', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO django_migrations (app, name, applied) 
VALUES ('plan_management', '0003_extend_notification_event_types', NOW())
ON CONFLICT DO NOTHING;
```

## ✅ 验证迁移

```sql
-- 检查表是否创建
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'plan_todo';

-- 查看表结构
\d plan_todo

-- 检查迁移记录
SELECT * FROM django_migrations 
WHERE app = 'plan_management' 
AND name IN ('0002_add_todo_model', '0003_extend_notification_event_types');
```

## 📋 迁移内容

### 0002_add_todo_model
- 创建 `plan_todo` 表
- 创建4个索引
- 添加外键约束

### 0003_extend_notification_event_types
- 扩展 `plan_approval_notification.event` 字段的选择项
- 扩展 `plan_approval_notification.object_type` 字段的选择项

## ⚠️ 注意事项

1. **备份数据库**：执行前请备份
2. **权限检查**：确保有CREATE TABLE权限
3. **记录迁移**：使用SQL脚本后必须记录到django_migrations表
4. **测试环境**：建议先在测试环境验证

## 🔧 故障排除

如果遇到问题，查看详细文档：
- `RUN_MIGRATIONS.md` - 详细迁移指南
- `MIGRATION_INSTRUCTIONS.md` - 迁移说明
