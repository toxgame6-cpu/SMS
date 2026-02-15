// =============================================================
// STUDENT MANAGEMENT SYSTEM — Main JavaScript
// =============================================================

// ===== THEME MANAGEMENT =====
function getStoredTheme() {
  return localStorage.getItem('sms-theme') || 'light';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('sms-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  setTheme(next);
}

// Initialize theme on load
document.addEventListener('DOMContentLoaded', function () {
  setTheme(getStoredTheme());
});

// ===== SIDEBAR =====
function toggleSidebarCollapse() {
  const sidebar = document.getElementById('sidebar');
  const collapseIcon = document.getElementById('collapseIcon');

  if (sidebar) {
    sidebar.classList.toggle('collapsed');

    if (collapseIcon) {
      collapseIcon.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
    }

    localStorage.setItem('sms-sidebar-collapsed', sidebar.classList.contains('collapsed'));
  }
}

function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (sidebar) {
    sidebar.classList.toggle('open');
  }
  if (overlay) {
    overlay.classList.toggle('active');
  }
}

function closeMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
}

// Restore sidebar state
document.addEventListener('DOMContentLoaded', function () {
  const isCollapsed = localStorage.getItem('sms-sidebar-collapsed') === 'true';
  const sidebar = document.getElementById('sidebar');
  const collapseIcon = document.getElementById('collapseIcon');

  if (isCollapsed && sidebar && window.innerWidth > 768) {
    sidebar.classList.add('collapsed');
    if (collapseIcon) collapseIcon.textContent = '▶';
  }

  // Show collapse button on desktop
  const collapseBtn = document.getElementById('collapseBtn');
  if (collapseBtn && window.innerWidth > 768) {
    collapseBtn.style.display = 'flex';
  }
});

// ===== TOAST MANAGEMENT =====
function dismissToast(toastEl) {
  if (!toastEl) return;
  toastEl.style.animation = 'toastSlideOut 0.3s ease forwards';
  setTimeout(() => toastEl.remove(), 300);
}

// Auto-dismiss toasts
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    document.querySelectorAll('.toast').forEach(function (toast, index) {
      setTimeout(() => dismissToast(toast), index * 100);
    });
  }, 5000);
});

// ===== BUTTON RIPPLE EFFECT =====
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.btn').forEach(function (btn) {
    btn.addEventListener('mousedown', function (e) {
      // Remove old ripples
      this.querySelectorAll('.ripple').forEach(r => r.remove());

      const ripple = document.createElement('span');
      ripple.className = 'ripple';

      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';

      this.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    });
  });
});

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function (e) {
  // Escape to close modals
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => {
      m.classList.remove('active');
    });
    closeMobileSidebar();
  }
});

// ===== CONFIRM DIALOG =====
function showConfirmDialog(message, actionUrl) {
  const dialog = document.getElementById('confirmDialog');
  const msg = document.getElementById('confirmMessage');
  const form = document.getElementById('confirmForm');
  if (dialog && msg && form) {
    msg.textContent = message;
    form.action = actionUrl;
    dialog.classList.add('active');
  }
}

function closeConfirmDialog() {
  const dialog = document.getElementById('confirmDialog');
  if (dialog) {
    dialog.classList.remove('active');
  }
}

// ===== LOADING SPINNER =====
function showLoading() {
  const el = document.getElementById('loading');
  if (el) el.style.display = 'flex';
}

function hideLoading() {
  const el = document.getElementById('loading');
  if (el) el.style.display = 'none';
}

// ===== MODAL HELPERS =====
function openModal(id) {
  const modal = document.getElementById('modal-' + id);
  if (modal) modal.classList.add('active');
}

function closeModal(id) {
  const modal = document.getElementById('modal-' + id);
  if (modal) modal.classList.remove('active');
}

// ===== ACCORDION TOGGLE =====
function toggleAccordion(id) {
  const el = document.getElementById(id);
  if (el) {
    const isOpen = el.style.display !== 'none';
    el.style.display = isOpen ? 'none' : 'block';
  }
}

// ===== SCROLL TO TOP =====
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== CLOSE MOBILE SIDEBAR ON RESIZE =====
window.addEventListener('resize', function () {
  if (window.innerWidth > 768) {
    closeMobileSidebar();
  }
});