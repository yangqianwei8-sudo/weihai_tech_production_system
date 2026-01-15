// 计划管理页面标题区域样式自动修复脚本
// 确保副标题显示在主标题右侧（右下角），底部对齐，并添加灰色线条，按钮位于线条右上角

(function() {
  function applySubtitleFix() {
    const wrapper = document.querySelector('.pm-page-header-title-wrapper');
    const actions = document.querySelector('.pm-page-header .pm-actions');
    
    if (wrapper) {
      // 强制应用flex布局
      wrapper.style.setProperty('display', 'flex', 'important');
      wrapper.style.setProperty('align-items', 'flex-end', 'important');
      wrapper.style.setProperty('gap', '12px', 'important');
      wrapper.style.setProperty('padding-bottom', '8px', 'important');
      wrapper.style.setProperty('border-bottom', '1px solid #E0E0E0', 'important');
      wrapper.style.setProperty('margin-bottom', '8px', 'important');
      
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
      }
    }
    
    if (actions) {
      // 按钮区域也添加相同的线条和间距
      actions.style.setProperty('padding-bottom', '8px', 'important');
      actions.style.setProperty('border-bottom', '1px solid #E0E0E0', 'important');
      actions.style.setProperty('margin-bottom', '8px', 'important');
      actions.style.setProperty('align-self', 'flex-start', 'important');
    }
  }
  
  // 页面加载完成后立即应用
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applySubtitleFix);
  } else {
    applySubtitleFix();
  }
  
  // 监听DOM变化，确保动态内容也能应用样式
  const observer = new MutationObserver(function(mutations) {
    if (document.querySelector('.pm-page-header-title-wrapper')) {
      applySubtitleFix();
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
