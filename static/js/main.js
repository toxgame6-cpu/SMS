// ===== MAIN.JS - Complete Application Logic =====

document.addEventListener('DOMContentLoaded', function () {

    // ===== THEME MANAGEMENT =====
    initTheme();

    // ===== AUTO-HIDE TOASTS =====
    setTimeout(function () {
        document.querySelectorAll('.toast').forEach(function (toast, i) {
            setTimeout(function () {
                toast.style.transition = 'all 0.35s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(function () { toast.remove(); }, 350);
            }, i * 100);
        });
    }, 5000);

    // ===== RIPPLE EFFECT =====
    document.querySelectorAll('.btn, .stat-card').forEach(function (el) {
        el.addEventListener('click', createRipple);
    });

    // ===== 3D TILT ON STAT CARDS =====
    document.querySelectorAll('.stat-card').forEach(function (card) {
        card.addEventListener('mousemove', function (e) {
            var rect = card.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            var rx = ((y - rect.height / 2) / rect.height) * -6;
            var ry = ((x - rect.width / 2) / rect.width) * 6;
            card.style.transform = 'perspective(800px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) translateY(-4px)';
        });

        card.addEventListener('mouseleave', function () {
            card.style.transition = 'transform 0.4s ease';
            card.style.transform = 'perspective(800px) rotateX(0) rotateY(0) translateY(0)';
        });

        card.addEventListener('mouseenter', function () {
            card.style.transition = 'transform 0.08s ease';
        });
    });

    // ===== ANIMATE COUNTERS =====
    document.querySelectorAll('.stat-card .value').forEach(function (el) {
        var val = parseInt(el.textContent) || 0;
        if (val > 0) {
            el.textContent = '0';
            animateCounter(el, 0, val, 700);
        }
    });

    // ===== STAGGER ANIMATION =====
    var cards = document.querySelectorAll('.card, .stat-card');
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, idx) {
            if (entry.isIntersecting) {
                setTimeout(function () {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, idx * 60);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05 });

    cards.forEach(function (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(card);
    });

    // ===== KEYBOARD SHORTCUTS =====
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(function (m) {
                m.classList.remove('active');
            });
            closeMobileSidebar();
        }
    });

    // ===== SIDEBAR STATE RESTORE =====
    restoreSidebarState();

    // ===== SMOOTH PAGE LOAD =====
    document.body.style.opacity = '1';
});


// ===== THEME FUNCTIONS =====

function initTheme() {
    var saved = localStorage.getItem('sms-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
}

function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('sms-theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    var icon = document.getElementById('themeIcon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    var btn = document.getElementById('themeBtn');
    if (btn) {
        btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
}


// ===== SIDEBAR FUNCTIONS =====

function toggleSidebarCollapse() {
    var sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    sidebar.classList.toggle('collapsed');
    var isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sms-sidebar-collapsed', isCollapsed);

    var icon = document.getElementById('collapseIcon');
    if (icon) {
        icon.textContent = isCollapsed ? '▶' : '◀';
    }
}

function restoreSidebarState() {
    if (window.innerWidth <= 768) return;

    var collapsed = localStorage.getItem('sms-sidebar-collapsed') === 'true';
    var sidebar = document.getElementById('sidebar');
    if (sidebar && collapsed) {
        sidebar.classList.add('collapsed');
        var icon = document.getElementById('collapseIcon');
        if (icon) icon.textContent = '▶';
    }
}

function toggleMobileSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar) {
        sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('active', sidebar.classList.contains('open'));
    }
}

function closeMobileSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
}


// ===== RIPPLE EFFECT =====

function createRipple(e) {
    var el = this;
    var ripple = document.createElement('span');
    var rect = el.getBoundingClientRect();
    var size = Math.max(rect.width, rect.height);

    ripple.style.cssText =
        'position:absolute;border-radius:50%;pointer-events:none;' +
        'width:' + size + 'px;height:' + size + 'px;' +
        'left:' + (e.clientX - rect.left - size / 2) + 'px;' +
        'top:' + (e.clientY - rect.top - size / 2) + 'px;' +
        'background:rgba(255,255,255,0.12);transform:scale(0);' +
        'animation:rippleAnim 0.5s ease-out;';

    el.style.position = 'relative';
    el.style.overflow = 'hidden';
    el.appendChild(ripple);
    setTimeout(function () { ripple.remove(); }, 500);
}

// Add ripple animation keyframes
var rippleStyle = document.createElement('style');
rippleStyle.textContent = '@keyframes rippleAnim { to { transform: scale(4); opacity: 0; } }';
document.head.appendChild(rippleStyle);


// ===== COUNTER ANIMATION =====

function animateCounter(el, start, end, duration) {
    var startTime = performance.now();

    function update(now) {
        var elapsed = now - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(start + (end - start) * eased);
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = end;
        }
    }

    requestAnimationFrame(update);
}


// ===== TOAST =====

function showToast(message, type) {
    type = type || 'info';
    var container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    var icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML = (icons[type] || 'ℹ️') + ' ' + message;
    toast.style.cursor = 'pointer';
    toast.onclick = function () { this.remove(); };
    container.appendChild(toast);

    setTimeout(function () {
        toast.style.transition = 'all 0.35s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(function () { toast.remove(); }, 350);
    }, 5000);
}


// ===== MODAL =====

function openModal(id) {
    var modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    var modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modal on overlay click
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});


// ===== UTILITIES =====

function printPage() { window.print(); }

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        showToast('Copied to clipboard!', 'success');
    });
}