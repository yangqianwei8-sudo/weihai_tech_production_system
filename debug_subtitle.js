// 在浏览器控制台运行此脚本，自动获取HTML结构和CSS信息

console.log("=== 副标题调试信息 ===\n");

// 1. 获取实际HTML结构
const wrapper = document.querySelector('.pm-page-header-title-wrapper');
if (wrapper) {
  console.log("1. 实际HTML结构:");
  console.log(wrapper.outerHTML);
  console.log("\n");
  
  // 2. 获取计算后的样式
  const h1 = wrapper.querySelector('h1');
  const subtitle = wrapper.querySelector('.pm-subtitle');
  
  if (h1) {
    console.log("2. H1元素的计算样式:");
    const h1Styles = window.getComputedStyle(h1);
    console.log("  display:", h1Styles.display);
    console.log("  margin:", h1Styles.margin);
    console.log("  padding:", h1Styles.padding);
    console.log("  line-height:", h1Styles.lineHeight);
    console.log("\n");
  }
  
  if (subtitle) {
    console.log("3. 副标题元素的计算样式:");
    const subtitleStyles = window.getComputedStyle(subtitle);
    console.log("  display:", subtitleStyles.display);
    console.log("  margin:", subtitleStyles.margin);
    console.log("  padding:", subtitleStyles.padding);
    console.log("  position:", subtitleStyles.position);
    console.log("  top:", subtitleStyles.top);
    console.log("  right:", subtitleStyles.right);
    console.log("  bottom:", subtitleStyles.bottom);
    console.log("  left:", subtitleStyles.left);
    console.log("\n");
  }
  
  // 3. 获取wrapper的计算样式
  console.log("4. Wrapper元素的计算样式:");
  const wrapperStyles = window.getComputedStyle(wrapper);
  console.log("  display:", wrapperStyles.display);
  console.log("  flex-direction:", wrapperStyles.flexDirection);
  console.log("  align-items:", wrapperStyles.alignItems);
  console.log("  gap:", wrapperStyles.gap);
  console.log("\n");
  
  // 4. 检查所有应用的CSS规则
  console.log("5. 检查应用的CSS规则:");
  const sheet = document.styleSheets;
  let foundRules = [];
  
  for (let i = 0; i < sheet.length; i++) {
    try {
      const rules = sheet[i].cssRules || sheet[i].rules;
      if (rules) {
        for (let j = 0; j < rules.length; j++) {
          const rule = rules[j];
          if (rule.selectorText && (
            rule.selectorText.includes('pm-page-header') ||
            rule.selectorText.includes('pm-subtitle')
          )) {
            foundRules.push({
              selector: rule.selectorText,
              cssText: rule.cssText,
              style: rule.style.cssText
            });
          }
        }
      }
    } catch (e) {
      // 跨域样式表可能无法访问
    }
  }
  
  console.log("找到的CSS规则数量:", foundRules.length);
  foundRules.forEach((rule, index) => {
    console.log(`\n规则 ${index + 1}:`);
    console.log("  选择器:", rule.selector);
    console.log("  样式:", rule.style);
  });
  
} else {
  console.error("未找到 .pm-page-header-title-wrapper 元素");
  console.log("请检查页面是否使用了正确的模板");
}

// 6. 尝试强制应用样式（临时测试）
console.log("\n6. 尝试强制应用样式（临时测试）:");
if (wrapper) {
  wrapper.style.setProperty('display', 'flex', 'important');
  wrapper.style.setProperty('align-items', 'flex-end', 'important');
  wrapper.style.setProperty('gap', '12px', 'important');
  console.log("已强制应用flex布局，请查看页面是否变化");
}
