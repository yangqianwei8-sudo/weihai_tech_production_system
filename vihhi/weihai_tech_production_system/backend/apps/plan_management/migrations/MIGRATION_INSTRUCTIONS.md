# 数据库迁移说明

## 迁移文件

迁移文件 `0002_add_todo_model.py` 已创建，用于创建 `plan_todo` 表。

## 运行迁移

### 方法1：直接运行迁移命令

```bash
cd /workspace/vihhi/weihai_tech_production_system
python manage.py migrate plan_management
```

### 方法2：使用 Docker（如果使用 Docker 环境）

```bash
cd /workspace/vihhi/weihai_tech_production_system
docker-compose exec backend python manage.py migrate plan_management
```

### 方法3：查看迁移计划（不实际执行）

```bash
python manage.py migrate plan_management --plan
```

### 方法4：查看 SQL（查看将执行的 SQL 语句）

```bash
python manage.py migrate plan_management --sql
```

## 验证迁移

迁移成功后，可以验证表是否创建：

```sql
-- PostgreSQL
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'plan_todo';

-- 查看表结构
\d plan_todo
```

## 回滚迁移（如果需要）

如果需要回滚迁移：

```bash
python manage.py migrate plan_management 0001_initial
```

## 注意事项

1. 迁移前请备份数据库
2. 确保数据库连接正常
3. 确保有足够的数据库权限
4. 在生产环境运行前，建议先在测试环境验证
