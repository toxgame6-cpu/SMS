 
// ===== File Upload Handler =====
document.addEventListener('DOMContentLoaded', function() {
    const uploadZones = document.querySelectorAll('.upload-zone');

    uploadZones.forEach(function(zone) {
        const input = zone.querySelector('input[type="file"]');

        // Click to upload
        zone.addEventListener('click', function(e) {
            if (e.target !== input) {
                input.click();
            }
        });

        // Drag and drop
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#4f46e5';
            this.style.background = '#eef2ff';
        });

        zone.addEventListener('dragleave', function() {
            this.style.borderColor = '#d1d5db';
            this.style.background = '#f9fafb';
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#d1d5db';
            this.style.background = '#f9fafb';
            input.files = e.dataTransfer.files;
            updateFileInfo(input);
        });

        // File selection
        if (input) {
            input.addEventListener('change', function() {
                updateFileInfo(this);
            });
        }
    });
});

function updateFileInfo(input) {
    const zone = input.closest('.upload-zone');
    let info = zone.parentElement.querySelector('.file-info');

    if (!info) {
        info = document.createElement('div');
        info.className = 'file-info';
        info.style.cssText = 'margin-top:10px;padding:10px;background:#f0fdf4;border-radius:8px;font-size:13px;color:#16a34a;';
        zone.parentElement.appendChild(info);
    }

    if (input.files.length > 0) {
        const file = input.files[0];
        const size = (file.size / 1024).toFixed(1);
        info.innerHTML = `📎 ${file.name} (${size} KB)`;
        info.style.display = 'block';

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            info.style.background = '#fee2e2';
            info.style.color = '#dc2626';
            info.innerHTML = `❌ File too large: ${file.name} (${(file.size/1024/1024).toFixed(1)} MB). Max 10MB allowed.`;
        }
    }
}