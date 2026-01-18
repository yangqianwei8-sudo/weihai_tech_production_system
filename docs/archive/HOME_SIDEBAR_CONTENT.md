# 总工作台首页左侧栏完整内容

## 📋 左侧栏结构

### HTML模板结构（home_base.html）

```html
<aside class="vh-sb" aria-label="左侧栏（全屏固定）">
  <!-- 顶部标题区域 -->
  <div class="vh-sb__top">
    <div class="vh-sb__topInner">
      <div class="vh-sb__titleWrap">
        <div class="vh-sb__title">系统总工作台</div>
        <div class="vh-sb__sub">System Dashboard</div>
      </div>
    </div>
  </div>

  <!-- 导航菜单区域 -->
  <nav class="vh-sb__nav">
    <!-- 功能模块分组 -->
    <div class="vh-sb__group">
      <div class="vh-sb__gtitle">功能模块</div>
      
      <!-- 遍历菜单项 -->
      {% for menu_item in centers_navigation %}
        {% if menu_item.children %}
          <!-- 有子菜单的父级菜单项 -->
          <div class="vh-sb__parent">
            <a href="{{ menu_item.url }}" class="vh-sb__item vh-sb__item--parent">
              <span class="vh-sb__icon">{{ menu_item.icon|default:"▢" }}</span>
              <span class="vh-sb__label">{{ menu_item.label }}</span>
            </a>
            <div class="vh-sb__children">
              {% for child in menu_item.children %}
                <a href="{{ child.url }}" class="vh-sb__child">
                  <span class="vh-sb__icon">{{ child.icon|default:"·" }}</span>
                  <span class="vh-sb__label">{{ child.label }}</span>
                </a>
              {% endfor %}
            </div>
          </div>
        {% else %}
          <!-- 无子菜单的菜单项 -->
          <a href="{{ menu_item.url }}" class="vh-sb__item">
            <span class="vh-sb__icon">{{ menu_item.icon|default:"▢" }}</span>
            <span class="vh-sb__label">{{ menu_item.label }}</span>
          </a>
        {% endif %}
      {% endfor %}
    </div>

    <!-- 管理后台分组 -->
    <div class="vh-sb__group">
      <a href="{% url 'admin:index' %}" class="vh-sb__item">
        <span class="vh-sb__icon">⚙️</span>
        <span class="vh-sb__label">管理后台</span>
      </a>
    </div>
  </nav>

  <!-- 底部操作区域 -->
  <div class="vh-sb__bottom">
    <div class="vh-sb__mini">帮助</div>
    <div class="vh-sb__mini">设置</div>
    <div class="vh-sb__mini">反馈</div>
  </div>
</aside>
```

## 📝 菜单项数据源（HOME_NAV_STRUCTURE）

菜单项定义在 `backend/core/views.py` 的 `HOME_NAV_STRUCTURE` 中：

## 📝 菜单项列表（共15个功能模块）

根据 `HOME_NAV_STRUCTURE` 定义，左侧栏包含以下菜单项：

| 序号 | 图标 | 菜单名称 | URL路由名称 | 权限要求 |
|------|------|---------|------------|---------|
| 1 | 👥 | 客户管理 | `business_pages:customer_management_home` | `customer_management.client.view` |
| 2 | 💼 | 商机管理 | `business_pages:opportunity_management` | `customer_success.opportunity.view` |
| 3 | 📄 | 合同管理 | `business_pages:contract_management_list` | `customer_management.contract.view` |
| 4 | 💰 | 回款管理 | `settlement_pages:payment_plan_list` | `payment_management.payment_plan.view` |
| 5 | 🏗️ | 生产管理 | `production_pages:project_list` | `production_management.view_assigned` |
| 6 | 🗂️ | 资源管理 | `resource_standard_pages:standard_list` | `resource_center.view` |
| 7 | 🤝 | 任务协作 | `collaboration_pages:task_board` | `task_collaboration.view` |
| 8 | 📦 | 收发管理 | `delivery_pages:report_delivery` | `delivery_center.view` |
| 9 | 📁 | 档案管理 | `archive_management:archive_list` | `archive_management.view` |
| 10 | 📅 | 计划管理 | `plan_pages:plan_management_home` | `plan_management.view` |
| 11 | ⚖️ | 诉讼管理 | `litigation_pages:litigation_home` | `litigation_management.view` |
| 12 | ⚠️ | 风险管理 | `#` (占位，待实现) | `risk_management.view` |
| 13 | 💵 | 财务管理 | `finance_pages:financial_home` | `financial_management.view` |
| 14 | 👤 | 人事管理 | `personnel_pages:personnel_home` | `personnel_management.view` |
| 15 | 🏢 | 行政管理 | `admin_pages:administrative_home` | `administrative_management.view` |
| 16 | ⚙️ | 系统管理 | `system_pages:system_settings` | `system_management.view` |

### 特殊菜单项

- **管理后台**：固定显示在功能模块下方，链接到Django Admin后台
  - 图标：⚙️
  - URL：`{% url 'admin:index' %}`
  - 无权限要求（所有登录用户可见）

## 🔧 菜单构建逻辑

菜单通过 `_build_full_top_nav()` 函数构建：

1. **权限检查**：遍历 `HOME_NAV_STRUCTURE`，检查用户是否有对应权限
2. **URL解析**：将 `url_name` 转换为实际URL（使用Django的 `reverse()`）
3. **菜单生成**：生成包含 `label`、`icon`、`url` 的菜单项列表
4. **返回结果**：返回过滤后的菜单项列表（`centers_navigation`）

## 📐 左侧栏布局结构

```
┌─────────────────────────┐
│  系统总工作台           │ ← 顶部标题区域 (.vh-sb__top)
│  System Dashboard       │
├─────────────────────────┤
│ 功能模块                │ ← 分组标题 (.vh-sb__gtitle)
│ ├─ 👥 客户管理          │ ← 菜单项 (.vh-sb__item)
│ ├─ 💼 商机管理          │
│ ├─ 📄 合同管理          │
│ ├─ 💰 回款管理          │
│ ├─ 🏗️ 生产管理          │
│ ├─ 🗂️ 资源管理          │
│ ├─ 🤝 任务协作          │
│ ├─ 📦 收发管理          │
│ ├─ 📁 档案管理          │
│ ├─ 📅 计划管理          │
│ ├─ ⚖️ 诉讼管理          │
│ ├─ ⚠️ 风险管理          │
│ ├─ 💵 财务管理          │
│ ├─ 👤 人事管理          │
│ ├─ 🏢 行政管理          │
│ └─ ⚙️ 系统管理          │
├─────────────────────────┤
│ ⚙️ 管理后台             │ ← 管理后台分组 (.vh-sb__group)
└─────────────────────────┘
│ 帮助 | 设置 | 反馈      │ ← 底部操作区域 (.vh-sb__bottom)
└─────────────────────────┘
```

## 🎨 CSS类名说明

- `.vh-sb` - 侧边栏容器
- `.vh-sb__top` - 顶部标题区域
- `.vh-sb__title` - 主标题（系统总工作台）
- `.vh-sb__sub` - 副标题（System Dashboard）
- `.vh-sb__nav` - 导航菜单容器
- `.vh-sb__group` - 菜单分组
- `.vh-sb__gtitle` - 分组标题（功能模块）
- `.vh-sb__item` - 菜单项
- `.vh-sb__item--parent` - 父级菜单项（有子菜单）
- `.vh-sb__parent` - 父级菜单容器
- `.vh-sb__children` - 子菜单容器
- `.vh-sb__child` - 子菜单项
- `.vh-sb__icon` - 图标
- `.vh-sb__label` - 标签文字
- `.vh-sb__bottom` - 底部操作区域
- `.vh-sb__mini` - 底部操作项（帮助、设置、反馈）
- `.is-active` - 激活状态（当前页面）

## 📍 文件位置

- **HTML模板**：`backend/templates/shared/home_base.html`
- **菜单数据定义**：`backend/core/views.py` (第73-92行)
- **菜单构建函数**：`backend/core/views.py` (第95-128行)
- **样式文件**：`backend/static/css/components/sidebar_v2_fixed.css`

## ✅ 总结

左侧栏包含：
- **1个标题区域**：系统总工作台 / System Dashboard
- **1个功能模块分组**：包含15个功能模块菜单项（根据权限动态显示）
- **1个管理后台分组**：固定显示的管理后台入口
- **1个底部操作区域**：帮助、设置、反馈（3个操作项）

所有菜单项都会根据用户权限进行过滤，只有拥有相应权限的用户才能看到对应的菜单项。
