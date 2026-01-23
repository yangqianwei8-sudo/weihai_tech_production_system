# 检查迁移状态

## 方法1：使用检查脚本（推荐）

### 在Kubernetes Pod中执行

```bash
# 找到backend pod
kubectl get pods -n weihai-tech | grep backend

# 进入pod执行检查
kubectl exec -it <pod-name> -n weihai-tech -- python backend/apps/plan_management/migrations/check_migration_status.py
```

### 使用端口转发后执行

```bash
# 端口转发
kubectl port-forward svc/postgresql-service -n weihai-tech 5432:5432

# 在另一个终端执行检查
export DATABASE_URL="postgres://weihai_user:password123@localhost:5432/weihai_tech"
cd /workspace/vihhi/weihai_tech_production_system
python3 backend/apps/plan_management/migrations/check_migration_status.py
```

## 方法2：使用SQL脚本检查

### 在Kubernetes Pod中执行

```bash
kubectl exec -it <pod-name> -n weihai-tech -- psql -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/check_migration_status.sql
```

### 使用psql直接连接

```bash
psql -h <数据库地址> -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/check_migration_status.sql
```

## 方法3：手动SQL检查

连接到数据库后执行：

```sql
-- 1. 检查表是否存在
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'plan_todo';

-- 2. 如果表存在，查看表结构
\d plan_todo

-- 3. 检查迁移记录
SELECT name, applied
FROM django_migrations
WHERE app = 'plan_management'
AND name IN ('0002_add_todo_model', '0003_extend_notification_event_types');

-- 4. 检查表记录数
SELECT COUNT(*) FROM plan_todo;
```

## 预期结果

### 迁移完成的标准

1. ✅ `plan_todo` 表存在
2. ✅ 表有正确的字段结构（至少包含：id, todo_type, title, assignee_id, deadline, status, is_overdue等）
3. ✅ 表有4个索引
4. ✅ `django_migrations` 表中有 `0002_add_todo_model` 记录
5. ✅ `django_migrations` 表中有 `0003_extend_notification_event_types` 记录

### 如果迁移未完成

执行迁移：

```bash
# 在Pod中
python manage.py migrate plan_management

# 或使用SQL脚本
psql -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/0002_add_todo_model.sql
psql -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/0003_extend_notification_event_types.sql
```
