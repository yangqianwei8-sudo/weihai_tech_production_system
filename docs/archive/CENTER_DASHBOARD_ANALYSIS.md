# center_dashboard.html 模板分析

## 📋 模板概述

`center_dashboard.html` 是一个用于展示"中心/模块首页"的模板，与 `home.html`（总工作台首页）不同，它主要用于各个功能模块的首页展示。

## 🎨 设计风格

### 视觉特点
- **品牌色系**：深蓝色主题（`#142F5B` 和 `#1F3E7C`）
- **圆角设计**：大量使用圆角（16px-24px），与总工作台的直角风格不同
- **渐变效果**：Hero区域使用渐变背景
- **阴影效果**：卡片使用柔和的阴影
- **现代化设计**：相比总工作台更加现代化和视觉化

### 样式特点
- Hero区域：深蓝色渐变背景，白色文字
- 摘要卡片：白色背景，圆角18px，带阴影
- 区块：白色背景，圆角20px，带阴影
- 项目卡片：浅蓝色背景（`--brand-soft`），圆角16px

## 📊 模板结构

### 1. Hero区域（`.center-hero`）
```html
<div class="center-hero">
  <h1>{{ page_title }}</h1>
  <p>{{ description }}</p>
</div>
```
- 深蓝色渐变背景
- 显示页面标题和描述
- 带径向渐变遮罩效果

### 2. 摘要卡片区域（`.summary-card`）
```html
<div class="summary-card">
  <h3>{{ card.label }}</h3>
  <div class="value">{{ card.value }}</div>
  <div class="hint">{{ card.hint }}</div>
</div>
```
- 4列网格布局（响应式）
- 显示关键统计数据
- 包含标签、数值和提示信息

### 3. 区块区域（`.section-block`）
```html
<div class="section-block">
  <div class="section-title">{{ section.title }}</div>
  <div class="section-desc">{{ section.description }}</div>
  <div class="section-item">
    <h4>{{ item.label }}</h4>
    <p>{{ item.description }}</p>
    <a href="{{ item.url }}">{{ item.link_label }}</a>
  </div>
</div>
```
- 可包含多个区块
- 每个区块有标题、描述和操作按钮
- 区块内包含多个项目卡片
- 项目卡片显示标签、描述和链接

## 🔄 与 home.html 的区别

| 特性 | home.html (总工作台) | center_dashboard.html (模块首页) |
|------|---------------------|-------------------------------|
| **继承** | `home_base.html` → `two_column_layout_base.html` | `base.html` |
| **布局** | 两栏布局（侧边栏+主内容） | 单栏布局（容器） |
| **设计风格** | 黑白灰，直角设计 | 深蓝色主题，圆角设计 |
| **主要内容** | 统计卡片、快捷操作、待办任务、最近动态 | Hero区域、摘要卡片、功能区块 |
| **用途** | 系统总工作台首页 | 各功能模块的首页 |

## 📝 使用场景

根据代码搜索结果，这个模板可能用于：
1. **各功能模块的首页**（如项目中心、客户管理等）
2. **数据统计页面**（如产值分析等）
3. **模块概览页面**

## 🎯 数据结构

模板期望的上下文数据：

```python
context = {
    'page_title': '页面标题',
    'description': '页面描述',
    'summary_cards': [
        {
            'label': '标签',
            'value': '数值',
            'hint': '提示信息（可选）'
        }
    ],
    'sections': [
        {
            'title': '区块标题',
            'description': '区块描述',
            'action': {
                'url': '操作链接',
                'label': '操作标签'
            },
            'items': [
                {
                    'label': '项目标签',
                    'description': '项目描述',
                    'url': '项目链接',
                    'link_label': '链接标签（默认：进入模块 →）'
                }
            ]
        }
    ]
}
```

## ✅ 总结

`center_dashboard.html` 是一个**模块化、视觉化**的dashboard模板，主要用于：
- 各功能模块的首页展示
- 数据统计和概览页面
- 功能入口和导航页面

它与 `home.html`（总工作台）的区别在于：
- **设计风格**：更现代化、视觉化（深蓝色主题 vs 黑白灰）
- **布局结构**：单栏容器布局 vs 两栏布局
- **内容重点**：功能模块展示 vs 任务和统计
