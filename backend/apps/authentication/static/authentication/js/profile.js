document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize progress bars width from data attributes
    const progressBars = document.querySelectorAll('.progress-bar-fill, .progress-fill-enhanced');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width) {
            bar.style.width = width + '%';
        }
    });

    // Animate progress bars on scroll with enhanced effect
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '0px 0px -50px 0px'
    };

    const progressObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.getAttribute('data-width') || '65';
                entry.target.style.width = '0%';
                
                // Add a slight delay for better visual effect
                setTimeout(() => {
                    entry.target.style.width = targetWidth + '%';
                    
                    // Add a subtle bounce effect
                    setTimeout(() => {
                        entry.target.style.transform = 'scaleY(1.1)';
                        setTimeout(() => {
                            entry.target.style.transform = 'scaleY(1)';
                        }, 200);
                    }, 800);
                }, 200);
                
                progressObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    progressBars.forEach(bar => {
        progressObserver.observe(bar);
    });

    // Enhanced hover effects for cards
    const cards = document.querySelectorAll('.profile-card, .activity-section, .progress-section, .apps-section');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });

    // Add hover effect to activity items with improved animation
    const activityItems = document.querySelectorAll('.activity-item');
    activityItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8fafc';
            this.style.transform = 'translateX(5px)';
            this.style.transition = 'all 0.3s ease';
        });
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
            this.style.transform = 'translateX(0)';
        });
    });

    // Add click ripple effect to buttons
    const buttons = document.querySelectorAll('.quick-action-btn, .edit-profile-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add floating animation to profile picture
    const profilePicture = document.querySelector('.profile-picture');
    if (profilePicture) {
        let isHovering = false;
        
        profilePicture.addEventListener('mouseenter', function() {
            isHovering = true;
            this.style.animation = 'float 2s ease-in-out infinite';
        });
        
        profilePicture.addEventListener('mouseleave', function() {
            isHovering = false;
            this.style.animation = '';
        });
    }

    // Enhance app cards with stagger animation
    const appCards = document.querySelectorAll('.app-card, .app-card-enhanced');
    appCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });

    // Add stats counter animation
    const statNumbers = document.querySelectorAll('.stat-value, .h5');
    const statsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const text = target.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                
                if (!isNaN(number) && number > 0) {
                    animateNumber(target, 0, number, 1000);
                }
                
                statsObserver.unobserve(target);
            }
        });
    });

    statNumbers.forEach(stat => {
        statsObserver.observe(stat);
    });

    // Number animation function
    function animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        const originalText = element.textContent;
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(progress * (end - start) + start);
            
            element.textContent = originalText.replace(/\d+/, current);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    // Add smooth scroll behavior for internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Add CSS for ripple effect and animations
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(2deg); }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease forwards;
        opacity: 0;
        transform: translateY(30px);
    }
    
    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);