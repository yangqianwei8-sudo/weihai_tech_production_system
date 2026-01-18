# 总工作台首页HTML结构文件清单

## 📁 核心模板文件

### 1. 主页面文件
- **`backend/templates/home.html`** (430行)
  - 总工作台首页的主要内容
  - 继承自：`shared/home_base.html`
  - 包含：统计卡片、快捷操作、待办任务、最近动态

### 2. 基础模板文件
- **`backend/templates/shared/home_base.html`** (101行)
  - 总工作台首页的基础模板
  - 继承自：`shared/two_column_layout_base.html`
  - 定义：侧边栏、顶部导航、内容区域结构

- **`backend/templates/shared/two_column_layout_base.html`**
  - 两栏布局基础模板
  - 提供：左侧栏 + 主内容区的布局结构

### 3. 相关组件文件
- **`backend/templates/shared/_top_nav.html`**
  - 顶部导航栏组件
  - 被home_base.html引用

- **`backend/templates/shared/center_dashboard.html`** (176行)
  - 可能是另一个dashboard模板

### 4. 备份/历史文件
- **`backend/templates/home.html.deleted`** (5094行)
  - 已删除的旧版home.html（可能包含历史设计）

- **`backend/templates/home.html.backup_*`**
  - home.html的备份文件

## 📊 文件继承关系

```
two_column_layout_base.html
    ↑
home_base.html
    ↑
home.html
```

## 🎨 相关样式文件（需要查找）
- CSS文件可能在 `backend/static/css/` 目录下
- JavaScript文件可能在 `backend/static/js/` 目录下

