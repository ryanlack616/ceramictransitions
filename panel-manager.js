// Shared collapsible/draggable panel manager for both static viewers.
(function (global) {
  const STORAGE_KEY = 'ct_panel_layout_v2';
  const style = document.createElement('style');
  style.textContent = `
    .panel-grip{display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:28px;padding:4px 2px;border-bottom:1px solid var(--border);cursor:grab;touch-action:none;user-select:none;color:var(--text-dim);font:9px var(--mono);text-transform:uppercase;letter-spacing:.7px;}
    .panel-grip.dragging{cursor:grabbing;color:var(--accent);}
    .panel-grip-label{display:flex;align-items:center;gap:6px;min-width:0;}
    .panel-drag-icon{color:var(--accent);font-size:13px;letter-spacing:-2px;}
    .panel-grip-actions{display:flex;gap:3px;flex:0 0 auto;}
    .panel-grip button{background:none;border:1px solid var(--border);color:var(--text-dim);width:22px;height:20px;padding:0;border-radius:3px;cursor:pointer;font:12px var(--mono);line-height:14px;}
    .panel-grip button:hover,.panel-grip button:focus-visible{border-color:var(--accent);color:var(--accent);outline:none;}
    .panel-moved{right:auto!important;bottom:auto!important;transform:none!important;}
    .panel-collapsed{min-height:0!important;height:auto!important;overflow:hidden!important;}
    .panel-filter .panel-body{display:flex;align-items:center;gap:6px;}
    .panel-strip .panel-body{display:flex;gap:0;overflow-x:auto;scrollbar-width:thin;}
  `;
  document.head.appendChild(style);

  function readLayout() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch (_) { return {}; }
  }

  function writeLayout(layout) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(layout)); }
    catch (_) { /* private mode */ }
  }

  function resetPanel(panel, layout) {
    delete layout[panel.id];
    panel.style.left = '';
    panel.style.top = '';
    panel.style.right = '';
    panel.style.bottom = '';
    panel.style.transform = '';
    panel.classList.remove('panel-moved');
    panel.classList.remove('panel-collapsed');
    const body = panel.querySelector(':scope > .panel-body');
    if (body) body.hidden = false;
    const collapse = panel.querySelector(':scope > .panel-grip .panel-collapse');
    if (collapse) {
      collapse.textContent = '−';
      collapse.setAttribute('aria-expanded', 'true');
    }
    writeLayout(layout);
  }

  function setup(panel, title, className, layout) {
    if (!panel || panel.dataset.panelReady) return;
    panel.dataset.panelReady = 'true';
    panel.style.pointerEvents = 'auto';
    if (className) panel.classList.add(className);

    const grip = document.createElement('div');
    grip.className = 'panel-grip';
    grip.title = 'Drag to move. Double-click or use reset to restore the default position.';
    grip.innerHTML = `<span class="panel-grip-label"><span class="panel-drag-icon" aria-hidden="true">⠿</span><span class="panel-title">${title}</span></span><span class="panel-grip-actions"><button class="panel-reset" type="button" aria-label="Reset ${title} position">↺</button><button class="panel-collapse" type="button" aria-label="Collapse ${title}" aria-expanded="true">−</button></span>`;

    const body = document.createElement('div');
    body.className = 'panel-body';
    while (panel.firstChild) body.appendChild(panel.firstChild);
    panel.append(grip, body);

    const reset = grip.querySelector('.panel-reset');
    const collapse = grip.querySelector('.panel-collapse');
    reset.addEventListener('click', event => {
      event.stopPropagation();
      resetPanel(panel, layout);
    });
    collapse.addEventListener('click', event => {
      event.stopPropagation();
      const collapsed = !panel.classList.contains('panel-collapsed');
      panel.classList.toggle('panel-collapsed', collapsed);
      body.hidden = collapsed;
      collapse.textContent = collapsed ? '+' : '−';
      collapse.setAttribute('aria-expanded', String(!collapsed));
      layout[panel.id] = { ...(layout[panel.id] || {}), collapsed };
      writeLayout(layout);
    });

    let drag = null;
    grip.addEventListener('pointerdown', event => {
      if (event.target.closest('button')) return;
      const rect = panel.getBoundingClientRect();
      drag = { pointerId: event.pointerId, dx: event.clientX - rect.left, dy: event.clientY - rect.top };
      panel.setPointerCapture(event.pointerId);
      panel.style.right = 'auto';
      panel.style.bottom = 'auto';
      panel.style.transform = 'none';
      panel.classList.add('panel-moved');
      panel.style.zIndex = String(++setup.zIndex);
      grip.classList.add('dragging');
    });
    grip.addEventListener('pointermove', event => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      const maxX = Math.max(0, innerWidth - panel.offsetWidth);
      const maxY = Math.max(0, innerHeight - panel.offsetHeight);
      const left = Math.max(0, Math.min(maxX, event.clientX - drag.dx));
      const top = Math.max(0, Math.min(maxY, event.clientY - drag.dy));
      panel.style.left = `${left}px`;
      panel.style.top = `${top}px`;
      layout[panel.id] = { ...(layout[panel.id] || {}), left, top };
    });
    const endDrag = event => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      drag = null;
      grip.classList.remove('dragging');
      writeLayout(layout);
    };
    grip.addEventListener('pointerup', endDrag);
    grip.addEventListener('pointercancel', endDrag);
    grip.addEventListener('dblclick', event => {
      if (event.target.closest('button')) return;
      resetPanel(panel, layout);
    });

    const saved = layout[panel.id];
    if (saved && Number.isFinite(saved.left) && Number.isFinite(saved.top)) {
      panel.style.left = `${Math.min(saved.left, Math.max(0, innerWidth - panel.offsetWidth))}px`;
      panel.style.top = `${Math.min(saved.top, Math.max(0, innerHeight - panel.offsetHeight))}px`;
      panel.style.right = 'auto';
      panel.style.bottom = 'auto';
      panel.style.transform = 'none';
      panel.classList.add('panel-moved');
    }
    if (saved?.collapsed) {
      panel.classList.add('panel-collapsed');
      body.hidden = true;
      collapse.textContent = '+';
      collapse.setAttribute('aria-expanded', 'false');
    }
  }

  function init(panels) {
    const layout = readLayout();
    setup.zIndex = 100;
    panels.forEach(config => setup(document.getElementById(config.id), config.title, config.className, layout));
  }

  global.PanelManager = { init, reset: () => localStorage.removeItem(STORAGE_KEY) };
})(window);
