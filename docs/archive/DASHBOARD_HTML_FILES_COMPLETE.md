# 总工作台首页HTML结构文件完整清单

## 📁 核心模板文件（按继承关系）

### 1. 最底层基础模板
- **`backend/templates/shared/two_column_layout_base.html`** (约100行)
  - 两栏布局基础模板
  - 提供：HTML文档结构、Bootstrap引入、两栏布局框架
  - 定义blocks：
    - `title` - 页面标题
    - `sidebar_width` - 侧边栏宽度
    - `sidebar_content` - 侧边栏内容
    - `top_nav` - 顶部导航
    - `content` - 主内容区
    - `content_inner` - 内容内部
    - `extra_css` - 额外CSS
    - `extra_js` - 额外JavaScript

### 2. 中间层基础模板
- **`backend/templates/shared/home_base.html`** (101行)
  - 总工作台首页的基础模板
  - 继承自：`shared/two_column_layout_base.html`
  - 定义：
    - 侧边栏结构（系统总工作台导航）
    - 顶部导航引用
    - 主内容区域框架
  - 引入CSS：
    - `css/components/navigation.css`
    - `css/components/list_layout.css`
    - `css/components/sidebar_v2_fixed.css`

### 3. 主页面文件
- **`backend/templates/home.html`** (430行)
  - 总工作台首页的主要内容
  - 继承自：`shared/home_base.html`
  - 包含内容：
    - 统计卡片区域（`.dashboard-stats`）
    - 快捷操作区域（`.dashboard-quick-actions`）
    - 待办任务列表（`.dashboard-tasks`）
    - 最近动态（`.dashboard-activity`）

## 📦 相关组件文件

### 顶部导航组件
- **`backend/templates/shared/_top_nav.html`**
  - 顶部导航栏组件
  - 被 `home_base.html` 引用

### 侧边栏组件
- **`backend/templates/shared/sidebar_v2_wireframe_fixed.html`**
  - 侧边栏组件（可能被two_column_layout_base.html引用）

### 其他Dashboard模板
- **`backend/templates/shared/center_dashboard.html`** (176行)
  - 可能是另一个dashboard模板
  - 继承自：`base.html`
  - 包含：hero区域、摘要卡片等

## 🎨 相关样式文件

### CSS文件
- **`backend/static/css/common.css`**
  - 通用样式文件

- **`backend/static/css/components/navigation.css`**
  - 导航相关样式

- **`backend/static/css/components/list_layout.css`**
  - 列表布局样式

- **`backend/static/css/components/sidebar_v2_fixed.css`**
  - 侧边栏样式

- **`backend/static/css/components/two_column_layout.css`**
  - 两栏布局样式

### JavaScript文件
- **`backend/static/js/common-components.js`**
  - 通用组件JavaScript

- **`backend/static/js/common-utils.js`**
  - 通用工具函数

## 📄 备份/历史文件

### 备份文件
- **`backend/templates/home.html.backup_20260115_130652`** (11KB)
  - home.html的备份文件（2025-01-15 13:06:52）

### 历史文件
- **`backend/templates/home.html.deleted`** (249KB, 5094行)
  - 已删除的旧版home.html
  - 包含大量历史设计代码
  - 可能包含完整的旧版dashboard设计

## 📊 文件继承关系图

```
two_column_layout_base.html (基础布局)
    ↑
home_base.html (工作台基础模板)
    ↑
home.html (工作台主页面)
```

## 🔗 引用关系

```
home.html
  ├─ extends: shared/home_base.html
  └─ blocks:
      ├─ home_extra_css (样式)
      ├─ content_inner (主要内容)
      └─ extra_js (脚本)

home_base.html
  ├─ extends: shared/two_column_layout_base.html
  ├─ includes: shared/_top_nav.html
  └─ blocks:
      ├─ sidebar_content (侧边栏)
      ├─ top_nav (顶部导航)
      ├─ extra_css (样式)
      ├─ content (主内容)
      └─ extra_js (脚本)

two_column_layout_base.html
  ├─ includes: shared/sidebar_v2_wireframe_fixed.html (可选)
  └─ blocks:
      ├─ title (标题)
      ├─ sidebar_width (侧边栏宽度)
      ├─ sidebar_content (侧边栏内容)
      ├─ top_nav (顶部导航)
      ├─ content (主内容)
      ├─ extra_css (额外样式)
      └─ extra_js (额外脚本)
```

## 📝 关键Blocks说明

### home.html中使用的blocks：
- `home_extra_css` - Dashboard页面专用样式
- `content_inner` - Dashboard主要内容（统计卡片、快捷操作、任务列表等）

### home_base.html中定义的blocks：
- `sidebar_content` - 左侧导航栏（系统总工作台菜单）
- `top_nav` - 顶部导航栏
- `welcome_card` - 欢迎卡片（已清空，等待重新设计）
- `content_inner` - 主内容区域

### two_column_layout_base.html中定义的blocks：
- `title` - 页面标题
- `sidebar_width` - 侧边栏宽度（默认232px）
- `sidebar_content` - 侧边栏内容
- `top_nav` - 顶部导航
- `content` - 主内容区
- `content_inner` - 内容内部
- `extra_css` - 额外CSS
- `extra_js` - 额外JavaScript

## ✅ 总结

总工作台首页的HTML结构由以下文件组成：
1. **two_column_layout_base.html** - 提供基础布局框架
2. **home_base.html** - 提供工作台特定的侧边栏和导航
3. **home.html** - 提供工作台的具体内容（统计、任务等）
4. **相关组件文件** - 顶部导航、侧边栏等
5. **样式文件** - CSS和JavaScript文件

这些文件共同构成了总工作台首页的完整HTML结构。
