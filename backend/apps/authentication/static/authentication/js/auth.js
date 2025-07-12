// Password strength validation for registration form
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('id_password1');
    const confirmPasswordField = document.getElementById('id_password2');
    
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.getElementById('strengthBar');
            const strengthText = document.getElementById('strengthText');
            
            if (!strengthBar || !strengthText) return;
            
            let strength = 0;
            let message = '';
            
            if (password.length >= 8) strength += 1;
            if (password.match(/[a-z]/)) strength += 1;
            if (password.match(/[A-Z]/)) strength += 1;
            if (password.match(/[0-9]/)) strength += 1;
            if (password.match(/[^a-zA-Z0-9]/)) strength += 1;
            
            switch (strength) {
                case 0:
                case 1:
                    strengthBar.style.width = '20%';
                    strengthBar.style.background = '#ef4444';
                    message = 'Très faible';
                    break;
                case 2:
                    strengthBar.style.width = '40%';
                    strengthBar.style.background = '#f97316';
                    message = 'Faible';
                    break;
                case 3:
                    strengthBar.style.width = '60%';
                    strengthBar.style.background = '#eab308';
                    message = 'Moyen';
                    break;
                case 4:
                    strengthBar.style.width = '80%';
                    strengthBar.style.background = '#22c55e';
                    message = 'Fort';
                    break;
                case 5:
                    strengthBar.style.width = '100%';
                    strengthBar.style.background = '#16a34a';
                    message = 'Très fort';
                    break;
            }
            
            strengthText.textContent = message;
        });
    }
    
    // Password confirmation validation
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            const password1 = document.getElementById('id_password1').value;
            const password2 = this.value;
            
            if (password2 && password1 !== password2) {
                this.setCustomValidity('Les mots de passe ne correspondent pas');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});