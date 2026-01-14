# 副标题位置调试指南

## 快速调试步骤

### 方法1：使用调试脚本（推荐）

1. 打开浏览器，访问计划管理页面（如 `/plan/home/`）
2. 按 `F12` 打开开发者工具
3. 切换到 `Console`（控制台）标签
4. 复制并运行以下代码：

```javascript
// 获取实际HTML结构和CSS信息
const wrapper = document.querySelector('.pm-page-header-title-wrapper');
if (wrapper) {
  console.log("=== HTML结构 ===");
  console.log(wrapper.outerHTML);
  
  console.log("\n=== 计算样式 ===");
  const styles = window.getComputedStyle(wrapper);
  console.log("display:", styles.display);
  console.log("align-items:", styles.alignItems);
  console.log("flex-direction:", styles.flexDirection);
  
  // 强制应用样式（临时测试）
  wrapper.style.setProperty('display', 'flex', 'important');
  wrapper.style.setProperty('align-items', 'flex-end', 'important');
  wrapper.style.setProperty('gap', '12px', 'important');
  console.log("\n已强制应用flex布局，请查看页面是否变化");
} else {
  console.error("未找到元素");
}
```

5. 查看控制台输出，将结果复制给我

### 方法2：手动检查

1. 打开浏览器开发者工具（F12）
2. 点击 Elements 标签
3. 使用选择器工具（左上角的箭头图标）点击页面上的"计划管理"标题
4. 在右侧 Styles 面板中：
   - 找到 `.pm-page-header-title-wrapper` 的样式
   - 查看是否有 `display: flex` 规则
   - 查看是否有被划掉的规则（表示被覆盖）
5. 截图或复制被划掉的CSS规则

### 方法3：检查模板文件

确认页面实际使用的模板：

1. 在浏览器中右键点击页面 → "查看网页源代码"
2. 搜索 `pm-page-header-title-wrapper`
3. 如果找不到，说明可能使用了不同的模板

## 预期效果

修改后，副标题应该显示为：

```
计划管理  管理工作计划和战略目标
```

（副标题在主标题的右侧，同一行，稍微靠下）

## 如果还是没有变化

请提供以下信息：

1. **实际HTML结构**：在Elements面板中，右键点击 `.pm-page-header-title-wrapper` → Copy → Copy outerHTML
2. **被覆盖的CSS规则**：在Styles面板中，找到被划掉的规则（通常有删除线）
3. **浏览器信息**：浏览器类型和版本
4. **页面URL**：当前访问的具体页面地址
