 
// ===== Password Visibility Toggle =====
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.toggle-password').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const input = document.getElementById(this.dataset.target);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '🙈';
                } else {
                    input.type = 'password';
                    this.textContent = '👁️';
                }
            }
        });
    });

    // Password strength checker
    const passwordInput = document.getElementById('new-password');
    const strengthBar = document.getElementById('password-strength');

    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (password.length >= 12) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;

            const colors = ['#dc2626', '#f59e0b', '#eab308', '#22c55e', '#16a34a'];
            const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];

            strengthBar.style.width = (strength * 20) + '%';
            strengthBar.style.background = colors[strength - 1] || '#e2e8f0';
            strengthBar.textContent = labels[strength - 1] || '';
        });
    }
});