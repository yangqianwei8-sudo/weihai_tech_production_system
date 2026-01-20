// Debug script for two-column-layout content overflow issue
// Run this in browser console on the problematic page

(function() {
  const logEndpoint = 'http://localhost:7242/ingest/8da7066a-e0c2-4e09-9af7-37ab2ebaf22c';
  
  function log(hypothesisId, message, data) {
    const payload = {
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: hypothesisId,
      location: 'debug_layout.js',
      message: message,
      data: data,
      timestamp: Date.now()
    };
    
    fetch(logEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
  }
  
  // Hypothesis A: .two-column-layout container height is too small
  const layout = document.querySelector('.two-column-layout');
  if (layout) {
    const layoutRect = layout.getBoundingClientRect();
    const layoutStyle = window.getComputedStyle(layout);
    log('A', 'Layout container dimensions', {
      width: layoutRect.width,
      height: layoutRect.height,
      minHeight: layoutStyle.minHeight,
      display: layoutStyle.display,
      flexDirection: layoutStyle.flexDirection,
      viewportHeight: window.innerHeight,
      calculatedMinHeight: window.innerHeight - 56
    });
  }
  
  // Hypothesis B: .two-col-main doesn't contain content properly
  const main = document.querySelector('.two-col-main');
  if (main) {
    const mainRect = main.getBoundingClientRect();
    const mainStyle = window.getComputedStyle(main);
    const mainContentHeight = main.scrollHeight;
    log('B', 'Main container dimensions', {
      width: mainRect.width,
      height: mainRect.height,
      scrollHeight: mainContentHeight,
      minHeight: mainStyle.minHeight,
      marginLeft: mainStyle.marginLeft,
      overflowY: mainStyle.overflowY,
      position: mainStyle.position
    });
  }
  
  // Hypothesis C: .two-col-content min-height: 100% causes overflow
  const content = document.querySelector('.two-col-content');
  if (content) {
    const contentRect = content.getBoundingClientRect();
    const contentStyle = window.getComputedStyle(content);
    const contentScrollHeight = content.scrollHeight;
    const parentHeight = content.parentElement ? content.parentElement.getBoundingClientRect().height : 0;
    log('C', 'Content container dimensions', {
      width: contentRect.width,
      height: contentRect.height,
      scrollHeight: contentScrollHeight,
      minHeight: contentStyle.minHeight,
      parentHeight: parentHeight,
      paddingTop: contentStyle.paddingTop,
      paddingBottom: contentStyle.paddingBottom,
      overflow: contentStyle.overflow
    });
  }
  
  // Hypothesis D: Content elements are positioned outside container
  const firstContentChild = content ? content.firstElementChild : null;
  if (firstContentChild) {
    const childRect = firstContentChild.getBoundingClientRect();
    const childStyle = window.getComputedStyle(firstContentChild);
    log('D', 'First content child position', {
      top: childRect.top,
      left: childRect.left,
      width: childRect.width,
      height: childRect.height,
      position: childStyle.position,
      marginTop: childStyle.marginTop,
      parentTop: content ? content.getBoundingClientRect().top : 0
    });
  }
  
  // Hypothesis E: Flex layout calculation issue
  if (layout && main) {
    const sidebar = document.querySelector('.two-col-sidebar');
    const sidebarWidth = sidebar ? sidebar.getBoundingClientRect().width : 0;
    const sidebarStyle = sidebar ? window.getComputedStyle(sidebar) : null;
    log('E', 'Flex layout calculation', {
      layoutWidth: layout.getBoundingClientRect().width,
      mainWidth: main.getBoundingClientRect().width,
      mainMarginLeft: window.getComputedStyle(main).marginLeft,
      sidebarWidth: sidebarWidth,
      sidebarPosition: sidebarStyle ? sidebarStyle.position : 'none',
      expectedMainWidth: layout.getBoundingClientRect().width - sidebarWidth - 8
    });
  }
  
  console.log('Debug logs sent. Check .cursor/debug.log file.');
})();
