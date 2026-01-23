# 迁移执行状态

## 当前情况

数据库地址是 Kubernetes 集群内的服务地址：
```
postgresql-service.weihai-tech.svc.cluster.local:5432
```

**无法从当前环境直接访问**，因为这是集群内部服务地址。

## 解决方案

### 方案1：在Kubernetes Pod中执行（推荐）

如果有kubectl访问权限，可以在Pod中执行：

```bash
# 找到backend pod
kubectl get pods -n weihai-tech | grep backend

# 进入pod执行迁移
kubectl exec -it <pod-name> -n weihai-tech -- python manage.py migrate plan_management
```

### 方案2：使用数据库端口转发

如果有kubectl访问权限，可以端口转发：

```bash
# 端口转发
kubectl port-forward svc/postgresql-service -n weihai-tech 5432:5432

# 在另一个终端执行迁移
export DATABASE_URL="postgres://weihai_user:password123@localhost:5432/weihai_tech"
python manage.py migrate plan_management
```

### 方案3：直接执行SQL脚本

如果有数据库的直接访问权限（通过公网IP或其他方式）：

```bash
# 使用psql连接
psql -h <数据库公网IP> -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/0002_add_todo_model.sql
psql -h <数据库公网IP> -U weihai_user -d weihai_tech -f backend/apps/plan_management/migrations/0003_extend_notification_event_types.sql
```

### 方案4：在部署时自动执行

在部署脚本中添加迁移步骤：

```bash
# 在部署脚本中
python manage.py migrate plan_management
```

## 迁移文件状态

✅ 所有迁移文件已准备就绪：
- `0002_add_todo_model.py` - Django迁移文件
- `0002_add_todo_model.sql` - SQL脚本
- `0003_extend_notification_event_types.py` - Django迁移文件  
- `0003_extend_notification_event_types.sql` - SQL脚本

✅ 迁移文件已验证通过

## 建议

**最佳实践**：在部署流程中自动执行迁移，或在Kubernetes Pod中手动执行。

迁移文件已完全准备好，只需要在有数据库访问权限的环境中执行即可。
