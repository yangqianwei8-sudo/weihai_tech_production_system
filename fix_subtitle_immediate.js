// 立即修复副标题位置的脚本 - 在浏览器控制台运行
(function() {
  const wrapper = document.querySelector('.pm-page-header-title-wrapper');
  if (!wrapper) {
    console.error('未找到 .pm-page-header-title-wrapper 元素');
    return;
  }
  
  // 强制应用所有样式
  wrapper.style.setProperty('display', 'flex', 'important');
  wrapper.style.setProperty('align-items', 'baseline', 'important');
  wrapper.style.setProperty('gap', '12px', 'important');
  
  const h1 = wrapper.querySelector('h1');
  if (h1) {
    h1.style.setProperty('margin', '0', 'important');
    h1.style.setProperty('padding', '0', 'important');
    h1.style.setProperty('line-height', '1.2', 'important');
  }
  
  const subtitle = wrapper.querySelector('.pm-subtitle');
  if (subtitle) {
    subtitle.style.setProperty('display', 'inline-block', 'important');
    subtitle.style.setProperty('margin', '0', 'important');
    subtitle.style.setProperty('padding', '0', 'important');
    subtitle.style.setProperty('line-height', '1.2', 'important');
    subtitle.style.setProperty('vertical-align', 'baseline', 'important');
  }
  
  console.log('✅ 已强制应用样式，副标题应该显示在主标题右侧');
})();
