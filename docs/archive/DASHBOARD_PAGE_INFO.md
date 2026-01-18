# Dashboard页面定位信息

## 📍 页面路由
- **URL路径**: `/` 或 `/dashboard/`
- **视图函数**: `backend.core.views.home()` / `backend.core.views.dashboard()`
- **路由配置**: `backend/config/urls.py` (第37-38行)

## 📁 关键文件清单

### 1. 视图文件
- **主视图**: `backend/core/views.py`
  - `home()` - 系统首页视图（第186行）
  - `dashboard()` - Dashboard视图（第406行，直接调用home）
  
- **API接口**: `backend/core/dashboard_views.py`
  - `dashboard_stats()` - 获取统计数据API（第15行）
  - `dashboard_todos()` - 获取待办事项API（第133行）

### 2. 模板文件
- **主模板**: `backend/templates/home.html` (430行)
  - 继承自: `shared/home_base.html`
  - 包含: 统计卡片、快捷操作、待办任务、最近动态
  
- **基础模板**: `backend/templates/shared/home_base.html`
  - 提供页面基础结构和导航

### 3. URL配置
- **主路由**: `backend/config/urls.py`
  - 第37行: `path('', home, name='home')`
  - 第38行: `path('dashboard/', dashboard, name='dashboard')`
  - 第59行: `path('api/admin/dashboard/stats/', dashboard_stats, name='dashboard_stats')`
  - 第60行: `path('api/admin/dashboard/todos/', dashboard_todos, name='dashboard_todos')`

## 🎨 页面结构

### 主要区块
1. **统计卡片区域** (`.dashboard-stats`)
   - 待办任务数
   - 进行中项目
   - 本月完成
   - 待审批任务
   - 待处理事项

2. **快捷操作区域** (`.dashboard-quick-actions`)
   - 创建计划
   - 创建项目
   - 项目列表
   - 计划列表
   - 系统设置

3. **主要内容区域** (`.dashboard-main`)
   - **待办任务列表** (`.dashboard-tasks`)
     - 待处理任务
     - 进行中任务
   - **最近动态** (`.dashboard-activity`)
     - 已完成任务记录

## 📊 数据来源

### 视图函数提供的数据
- `pending_counts`: 待办任务统计
- `approval_stats`: 审批统计
- `delivery_stats`: 交付统计
- `stats_cards`: 统计卡片数组
- `task_board`: 任务看板数据
  - `pending`: 待处理任务
  - `in_progress`: 进行中任务
  - `completed`: 已完成任务

### API接口
- `/api/admin/dashboard/stats/` - 统计数据
- `/api/admin/dashboard/todos/` - 待办事项

## 🎯 样式特点
- 简洁、清晰、整齐、稳重、美观
- 黑白灰配色
- 直角设计（border-radius: 0）
- 统一的卡片样式和间距

## ✅ 准备就绪
所有文件已定位，可以开始改造工作！
