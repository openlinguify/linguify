/**
 * Modern Blog Comments System - Reddit Style
 * OpenLinguify Blog Platform
 * 
 * Features:
 * - Real-time likes/unlikes
 * - Nested replies with smooth animations
 * - Report system with modal
 * - Form validation
 * - User experience enhancements
 */

class BlogCommentsSystem {
    constructor() {
        // Profanity filter - focused on real insults and vulgar language
        this.profanityWords = [
            // English - real insults and vulgar terms
            'fuck', 'shit', 'bitch', 'bastard', 'asshole', 
            'whore', 'slut', 'dick', 'cock', 'pussy', 'cunt',
            'fag', 'faggot', 'nigger', 'motherfucker',
            'twat', 'scumbag', 'douchebag', 'dickhead', 'prick',
            'fck', 'fuk', 'btch', 'sht', 'fukk', 'fucc', 'shyt',
            
            // French - real insults and vulgar terms (refined list)
            'merde', 'putain', 'connard', 'salope', 'pute', 'enculé',
            'bite', 'con', 'conne', 'crétin', 'débile', 'abruti', 'taré',
            'foutre', 'chier', 'bordel', 'bâtard', 'bâtarde', 'salaud',
            'salopard', 'saloperie', 'pédé', 'tapette', 'lopette', 'tarlouze',
            'bougnoule', 'bicot', 'raton', 'négro', 'nègre', 'chintok',
            'youpin', 'feuj', 'connasse', 'encule', 'enculer', 'fdp',
            'fils de pute', 'ptain', 'putin', 'ptn', 'batard', 'batarde',
            
            // Phonetic variations (essential only)
            'putin', 'poutain', 'putein', 'conar', 'salop', 'ankule',
            'fuk', 'fok', 'phuck', 'biatch', 'bytch',
            
            // Spanish - essential vulgar terms
            'joder', 'mierda', 'puta', 'cabrón', 'pendejo',
            'gilipollas', 'coño', 'hostia',
            
            // Dutch - essential vulgar terms
            'kut', 'klootzak', 'hoer', 'lul', 'pik', 'eikel',
            'mongool', 'debiel', 'kanker'
        ];
        
        this.init();
        this.bindEvents();
        this.setupFormValidation();
    }

    init() {
        console.group('🚀 Blog Comments System - Initialization');
        console.log('⚙️ Starting initialization...');
        
        // CSRF Token check
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (this.csrfToken) {
            console.log('✅ CSRF Token found:', this.csrfToken.substring(0, 10) + '...');
        } else {
            console.warn('⚠️ CSRF Token not found - AJAX requests may fail');
        }
        
        // User session
        this.userSession = this.loadUserSession();
        console.log('👤 User session loaded:', {
            hasName: !!this.userSession.name,
            hasEmail: !!this.userSession.email,
            likedCommentsCount: this.userSession.likedComments.length
        });
        
        // Initialize liked buttons
        this.initializeLikedButtons();
        console.log('✅ Blog Comments System initialized successfully');
        console.groupEnd();
    }
    
    initializeLikedButtons() {
        // Mark already liked comments
        if (this.userSession.likedComments && this.userSession.likedComments.length > 0) {
            this.userSession.likedComments.forEach(commentId => {
                const btn = document.querySelector(`.like-btn[data-comment-id="${commentId}"]`);
                if (btn) {
                    this.toggleLikeUI(btn, true);
                }
            });
        }
    }

    loadUserSession() {
        // Load user session from localStorage for likes/dislikes persistence
        return {
            name: localStorage.getItem('blog_user_name') || '',
            email: localStorage.getItem('blog_user_email') || '',
            likedComments: JSON.parse(localStorage.getItem('blog_liked_comments') || '[]')
        };
    }

    saveUserSession() {
        localStorage.setItem('blog_user_name', this.userSession.name);
        localStorage.setItem('blog_user_email', this.userSession.email);
        localStorage.setItem('blog_liked_comments', JSON.stringify(this.userSession.likedComments));
    }

    bindEvents() {
        console.log('🔧 Binding events...');
        
        // Like button functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.like-btn')) {
                console.log('👍 Like button clicked');
                e.preventDefault();
                this.handleLike(e.target.closest('.like-btn'));
            }
        });

        // Reply button functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.reply-btn')) {
                console.log('💬 Reply button clicked');
                e.preventDefault();
                this.handleReply(e.target.closest('.reply-btn'));
            }
        });

        // Cancel reply functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.cancel-reply')) {
                console.log('❌ Cancel reply clicked');
                e.preventDefault();
                this.handleCancelReply(e.target.closest('.cancel-reply'));
            }
        });

        // Submit reply functionality
        document.addEventListener('submit', (e) => {
            if (e.target.closest('.quick-reply-form')) {
                console.log('📨 Reply form submitted');
                e.preventDefault();
                this.handleSubmitReply(e.target.closest('.quick-reply-form'));
            }
        });

        // Report button functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.report-comment')) {
                console.log('🚩 Report button clicked');
                e.preventDefault();
                this.handleReport(e.target.closest('.report-comment'));
            }
        });

        // Share button functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.share-btn')) {
                console.log('🔗 Share button clicked');
                e.preventDefault();
                this.handleShare(e.target.closest('.share-btn'));
            }
        });

        // Collapse/Expand button functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.collapse-btn')) {
                console.log('🔧 Collapse button clicked');
                e.preventDefault();
                this.handleCollapseToggle(e.target.closest('.collapse-btn'));
            }
        });

        // Initialize collapse controls
        this.initializeCollapseControls();

        // Collapse summary click functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('.collapse-summary')) {
                console.log('📁 Collapse summary clicked');
                e.preventDefault();
                this.handleCollapseSummaryClick(e.target.closest('.collapse-summary'));
            }
        });

        // Report form submission
        const reportForm = document.getElementById('reportForm');
        if (reportForm) {
            console.log('📋 Report form found, binding submit event');
            reportForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmitReport();
            });
        } else {
            console.warn('⚠️ Report form not found');
        }

        // Sorting functionality
        const sortButtons = document.querySelectorAll('[data-sort]');
        console.log(`🔄 Found ${sortButtons.length} sort buttons`);
        sortButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSort(btn.dataset.sort);
                
                // Update active state
                sortButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    setupFormValidation() {
        // Main comment form validation
        const mainForm = document.getElementById('commentForm');
        if (mainForm) {
            this.setupMainFormValidation(mainForm);
        }

        // Character counter for all textareas (except main form which has its own)
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            // Skip the main comment form textarea as it already has a counter
            if (textarea.id !== 'commentContent') {
                this.setupCharacterCounter(textarea);
            }
        });
    }

    setupMainFormValidation(form) {
        const contentTextarea = form.querySelector('#commentContent');
        const charCount = document.getElementById('charCount');
        const submitBtn = document.getElementById('submitBtn');

        if (contentTextarea && charCount && submitBtn) {
            contentTextarea.addEventListener('input', () => {
                const count = contentTextarea.value.length;
                charCount.textContent = count;
                
                // Update button state and styling
                if (count < 10 || count > 1000) {
                    submitBtn.disabled = true;
                    charCount.style.color = '#e74c3c';
                    charCount.classList.add('text-danger');
                } else {
                    submitBtn.disabled = false;
                    charCount.style.color = '#27ae60';
                    charCount.classList.remove('text-danger');
                    charCount.classList.add('text-success');
                }
            });

            // Form submission validation
            form.addEventListener('submit', (e) => {
                if (!this.validateMainForm(form)) {
                    e.preventDefault();
                } else {
                    this.handleMainFormSubmit(submitBtn);
                }
            });
        }
    }

    setupCharacterCounter(textarea) {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        if (!maxLength) return;

        // Check if a counter already exists (for reply forms)
        let counter = textarea.parentNode.querySelector('.char-counter');
        
        // Only create a new counter if one doesn't exist
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'char-counter text-muted mt-1';
            counter.innerHTML = `<span class="current">0</span>/${maxLength} characters`;
            textarea.parentNode.appendChild(counter);
        }
        
        // Find the current count span - handle both formats
        let currentSpan = counter.querySelector('.current') || counter.querySelector('#charCount');
        
        textarea.addEventListener('input', () => {
            const current = textarea.value.length;
            if (currentSpan) {
                currentSpan.textContent = current;
            }
            
            if (current > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    }

    validateMainForm(form) {
        const name = form.querySelector('[name="author_name"]').value.trim();
        const email = form.querySelector('[name="author_email"]').value.trim();
        const content = form.querySelector('[name="content"]').value.trim();

        if (name.length < 2 || name.length > 100) {
            this.showNotification('Name must be between 2 and 100 characters', 'error');
            return false;
        }

        if (!this.isValidEmail(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return false;
        }

        if (content.length < 10 || content.length > 1000) {
            this.showNotification('Comment must be between 10 and 1000 characters', 'error');
            return false;
        }

        // Note: Profanity validation is handled server-side only
        // This prevents double messages and ensures consistency

        // Save user info for future use
        this.userSession.name = name;
        this.userSession.email = email;
        this.saveUserSession();

        return true;
    }

    handleMainFormSubmit(submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    }

    async handleLike(btn) {
        const commentId = btn.dataset.commentId;
        console.group(`👍 Like Handler - Comment ${commentId}`);
        console.log('🎯 Button clicked:', btn);
        
        // Check if user info is available
        if (!this.userSession.name || !this.userSession.email) {
            console.log('❓ User info missing, prompting for details...');
            const userInfo = await this.promptUserInfo('like this comment');
            if (!userInfo) {
                console.log('❌ User cancelled info prompt');
                console.groupEnd();
                return;
            }
            
            this.userSession.name = userInfo.name;
            this.userSession.email = userInfo.email;
            this.saveUserSession();
            console.log('✅ User info saved:', { name: userInfo.name, email: userInfo.email });
        }

        // Optimistic UI update
        const isLiked = this.userSession.likedComments.includes(commentId);
        console.log('📊 Current like status:', { commentId, isLiked, willBeLiked: !isLiked });
        this.toggleLikeUI(btn, !isLiked);

        try {
            console.log('🌐 Sending AJAX request to /blog/comment/like/');
            const requestData = {
                comment_id: commentId,
                author_name: this.userSession.name,
                author_email: this.userSession.email
            };
            console.log('📤 Request data:', requestData);
            
            // Create AbortController to prevent extension interference
            const abortController = new AbortController();
            const timeoutId = setTimeout(() => abortController.abort(), 10000); // 10 second timeout
            
            const response = await fetch('/blog/comment/like/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(requestData),
                signal: abortController.signal
            });
            
            clearTimeout(timeoutId);

            console.log('📥 Response status:', response.status, response.statusText);
            const data = await response.json();
            console.log('📄 Response data:', data);

            if (data.success) {
                // Update UI with server response
                this.updateLikeCount(btn, data.likes_count);
                console.log('✅ Like count updated to:', data.likes_count);
                
                // Update local storage
                if (data.liked) {
                    if (!this.userSession.likedComments.includes(commentId)) {
                        this.userSession.likedComments.push(commentId);
                    }
                } else {
                    this.userSession.likedComments = this.userSession.likedComments.filter(id => id !== commentId);
                }
                this.saveUserSession();
                console.log('💾 User session updated, liked comments:', this.userSession.likedComments);
                
                this.showNotification(data.liked ? 'Comment liked!' : 'Like removed', 'success');
            } else {
                console.error('❌ Server returned error:', data.error);
                // Revert optimistic update
                this.toggleLikeUI(btn, isLiked);
                this.showNotification(data.error || 'Failed to update like', 'error');
            }
        } catch (error) {
            console.error('💥 Network error:', error);
            // Revert optimistic update
            this.toggleLikeUI(btn, isLiked);
            this.showNotification('Network error. Please try again.', 'error');
        }
        
        console.groupEnd();
    }

    toggleLikeUI(btn, liked) {
        if (liked) {
            btn.classList.add('liked');
            btn.dataset.liked = 'true';
        } else {
            btn.classList.remove('liked');
            btn.dataset.liked = 'false';
        }
    }

    updateLikeCount(btn, count) {
        const countSpan = btn.querySelector('.like-count');
        if (countSpan) {
            countSpan.textContent = count;
            
            // Add bounce animation
            countSpan.style.transform = 'scale(1.2)';
            setTimeout(() => {
                countSpan.style.transform = 'scale(1)';
            }, 150);
        }
    }

    handleReply(btn) {
        const commentId = btn.dataset.commentId;
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        
        if (replyForm) {
            // Toggle form visibility with animation
            if (replyForm.style.display === 'none' || !replyForm.style.display) {
                replyForm.style.display = 'block';
                replyForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Pre-fill form if user info is available
                if (this.userSession.name) {
                    const nameField = replyForm.querySelector('[name="reply_author_name"]');
                    const emailField = replyForm.querySelector('[name="reply_author_email"]');
                    if (nameField) nameField.value = this.userSession.name;
                    if (emailField) emailField.value = this.userSession.email;
                }
                
                // Focus on content field
                const contentField = replyForm.querySelector('[name="reply_content"]');
                if (contentField) {
                    setTimeout(() => contentField.focus(), 100);
                }
            } else {
                replyForm.style.display = 'none';
            }
        }
    }

    handleCancelReply(btn) {
        const replyForm = btn.closest('.reply-form');
        replyForm.style.display = 'none';
        replyForm.querySelector('form').reset();
    }

    async handleSubmitReply(form) {
        const replyForm = form.closest('.reply-form');
        const commentId = replyForm.dataset.commentId;
        
        // Validate form
        const name = form.reply_author_name.value.trim();
        const email = form.reply_author_email.value.trim();
        const content = form.reply_content.value.trim();
        
        if (!name || !email || !content) {
            this.showNotification('All fields are required', 'error');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return;
        }
        
        if (content.length < 10) {
            this.showNotification('Reply must be at least 10 characters long', 'error');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('.submit-reply');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';

        try {
            console.log(`📤 Submitting reply to comment ${commentId}`);
            console.log(`📝 Reply data:`, { name, email, content: content.substring(0, 50) + '...', csrfToken: this.csrfToken ? 'present' : 'missing' });
            
            const formData = new FormData();
            formData.append('author_name', name);
            formData.append('author_email', email);
            formData.append('content', content);
            formData.append('csrfmiddlewaretoken', this.csrfToken);

            const url = `/blog/comment/${commentId}/reply/`;
            console.log(`🌐 Fetching URL: ${url}`);

            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            console.log(`📡 Response status: ${response.status} ${response.statusText}`);

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showNotification(data.message, 'success');
                    replyForm.style.display = 'none';
                    form.reset();
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    this.showNotification(data.message || 'Failed to submit reply', 'error');
                }
            } else {
                console.error(`❌ HTTP Error: ${response.status} ${response.statusText}`);
                const errorData = await response.json().catch((parseError) => {
                    console.error('❌ Failed to parse error response as JSON:', parseError);
                    return { message: 'Failed to submit reply' };
                });
                console.error('❌ Error data:', errorData);
                this.showNotification(errorData.message || 'Failed to submit reply', 'error');
            }
        } catch (error) {
            console.error('💥 Catch block error:', error);
            this.showNotification('Failed to submit reply. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    handleReport(btn) {
        const commentId = btn.dataset.commentId;
        console.log(`📝 Opening report modal for comment ${commentId}`);
        
        const reportCommentIdInput = document.getElementById('reportCommentId');
        if (reportCommentIdInput) {
            reportCommentIdInput.value = commentId;
        }
        
        // Pre-fill user info if available
        if (this.userSession.name) {
            const reporterNameInput = document.getElementById('reporterName');
            const reporterEmailInput = document.getElementById('reporterEmail');
            if (reporterNameInput) reporterNameInput.value = this.userSession.name;
            if (reporterEmailInput) reporterEmailInput.value = this.userSession.email;
        }
        
        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modalElement = document.getElementById('reportModal');
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                console.error('Report modal element not found');
                this.showNotification('Unable to open report form. Please refresh the page.', 'error');
            }
        } else {
            console.error('Bootstrap is not loaded');
            // Fallback: show modal manually
            const modalElement = document.getElementById('reportModal');
            if (modalElement) {
                modalElement.classList.add('show');
                modalElement.style.display = 'block';
                modalElement.setAttribute('aria-modal', 'true');
                modalElement.removeAttribute('aria-hidden');
                
                // Add backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                backdrop.id = 'report-modal-backdrop';
                document.body.appendChild(backdrop);
                document.body.classList.add('modal-open');
                
                // Add close functionality
                const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(closeBtn => {
                    closeBtn.addEventListener('click', () => {
                        this.closeReportModalManually();
                    });
                });
            } else {
                this.showNotification('Unable to open report form. Please refresh the page.', 'error');
            }
        }
    }
    
    closeReportModalManually() {
        const modalElement = document.getElementById('reportModal');
        if (modalElement) {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            modalElement.setAttribute('aria-hidden', 'true');
            modalElement.removeAttribute('aria-modal');
        }
        
        const backdrop = document.getElementById('report-modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        document.body.classList.remove('modal-open');
    }

    async handleSubmitReport() {
        const commentId = document.getElementById('reportCommentId').value;
        const reporterName = document.getElementById('reporterName').value.trim();
        const reporterEmail = document.getElementById('reporterEmail').value.trim();
        const reason = document.querySelector('input[name="reportReason"]:checked')?.value;
        const additionalInfo = document.getElementById('additionalInfo').value.trim();

        if (!reporterName || !reporterEmail || !reason) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        if (!this.isValidEmail(reporterEmail)) {
            this.showNotification('Please enter a valid email address', 'error');
            return;
        }

        try {
            const requestData = {
                comment_id: commentId,
                reporter_name: reporterName,
                reporter_email: reporterEmail,
                reason: reason,
                additional_info: additionalInfo
            };
            
            console.log('📤 Report request data:', requestData);
            
            const response = await fetch('/blog/comment/report/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(requestData)
            });

            console.log('📥 Report response status:', response.status, response.statusText);
            
            const data = await response.json();
            console.log('📄 Report response data:', data);

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Close modal
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const modalInstance = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                } else {
                    this.closeReportModalManually();
                }
                
                document.getElementById('reportForm').reset();
            } else {
                console.error('❌ Report failed:', data.error);
                this.showNotification(data.error || 'Failed to submit report', 'error');
            }
        } catch (error) {
            console.error('💥 Error submitting report:', error);
            this.showNotification('Failed to submit report. Please try again.', 'error');
        }
    }

    handleShare(btn) {
        const commentId = btn.dataset.commentId;
        const url = `${window.location.origin}${window.location.pathname}#comment-${commentId}`;
        
        console.log(`🔗 Sharing comment ${commentId} with URL: ${url}`);
        
        // Try native sharing first (mobile)
        if (navigator.share && /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            navigator.share({
                title: 'OpenLinguify Blog Comment',
                text: 'Check out this interesting comment on OpenLinguify blog',
                url: url
            }).then(() => {
                console.log('📱 Native share successful');
                this.showNotification('Comment shared successfully!', 'success');
            }).catch(err => {
                console.log('📱 Share cancelled or failed:', err);
                this.fallbackShare(btn, url);
            });
        } else {
            this.fallbackShare(btn, url);
        }
    }
    
    fallbackShare(btn, url) {
        // Desktop: Copy to clipboard with multiple fallbacks
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(() => {
                console.log('📋 Clipboard API successful');
                this.showShareSuccess(btn);
            }).catch(() => {
                console.log('📋 Clipboard API failed, trying fallback');
                this.legacyShareFallback(btn, url);
            });
        } else {
            this.legacyShareFallback(btn, url);
        }
    }
    
    showShareSuccess(btn) {
        this.showNotification('Comment link copied to clipboard!', 'success');
        
        // Visual feedback on button
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.classList.add('text-success');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('text-success');
        }, 2000);
    }
    
    legacyShareFallback(btn, url) {
        // Legacy fallback: create temporary input and select
        try {
            const tempInput = document.createElement('input');
            tempInput.value = url;
            document.body.appendChild(tempInput);
            tempInput.select();
            tempInput.setSelectionRange(0, 99999); // For mobile devices
            
            const successful = document.execCommand('copy');
            document.body.removeChild(tempInput);
            
            if (successful) {
                console.log('📋 Legacy copy successful');
                this.showShareSuccess(btn);
            } else {
                throw new Error('Copy command failed');
            }
        } catch (err) {
            console.error('📋 All copy methods failed:', err);
            // Last resort: show a prompt with the URL
            this.showUrlPrompt(url);
        }
    }
    
    showUrlPrompt(url) {
        // Show a modal or prompt with the URL for manual copying
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="modal fade" tabindex="-1" style="display: block; background: rgba(0,0,0,0.5);">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Share Comment</h5>
                            <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                        </div>
                        <div class="modal-body">
                            <p>Copy this link to share the comment:</p>
                            <div class="input-group">
                                <input type="text" class="form-control" value="${url}" readonly onclick="this.select()">
                                <button class="btn btn-primary" onclick="this.previousElementSibling.select(); document.execCommand('copy'); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Auto-select the URL
        const input = modal.querySelector('input');
        input.focus();
        input.select();
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    handleSort(sortType) {
        const container = document.querySelector('.comments-container');
        const comments = Array.from(container.querySelectorAll('.comment-depth-0'));
        
        comments.sort((a, b) => {
            switch(sortType) {
                case 'newest':
                    const dateA = new Date(a.dataset.createdAt || '0');
                    const dateB = new Date(b.dataset.createdAt || '0');
                    return dateB - dateA;
                    
                case 'oldest':
                    const dateA2 = new Date(a.dataset.createdAt || '0');
                    const dateB2 = new Date(b.dataset.createdAt || '0');
                    return dateA2 - dateB2;
                    
                case 'popular':
                    const likesA = parseInt(a.querySelector('.like-count')?.textContent || '0');
                    const likesB = parseInt(b.querySelector('.like-count')?.textContent || '0');
                    return likesB - likesA;
                    
                default:
                    return 0;
            }
        });
        
        // Clear and re-append sorted comments
        container.innerHTML = '';
        comments.forEach(comment => {
            container.appendChild(comment);
        });
        
        this.showNotification(`Comments sorted by ${sortType}`, 'info');
    }

    // =====================================
    // COLLAPSIBLE COMMENT SYSTEM
    // =====================================
    
    initializeCollapseControls() {
        console.log('🔧 Initializing collapse controls...');
        
        // Add collapse/expand buttons to comments with replies
        const comments = document.querySelectorAll('.comment-item');
        let controlsAdded = 0;
        
        comments.forEach(comment => {
            const replies = this.getDirectReplies(comment);
            if (replies.length > 0) {
                this.addCollapseControl(comment, replies.length);
                controlsAdded++;
                
                // Auto-collapse replies by default (except for top-level comments)
                const depth = parseInt(comment.dataset.depth || 0);
                if (depth >= 0) { // Collapse all threads including top-level
                    const collapseBtn = comment.querySelector('.collapse-btn');
                    if (collapseBtn && !collapseBtn.classList.contains('collapsed')) {
                        // Simulate click to collapse
                        setTimeout(() => {
                            this.handleCollapseToggle(collapseBtn, true); // true = initial load
                        }, 100);
                    }
                }
            }
        });
        
        console.log(`✅ Added ${controlsAdded} collapse controls`);
        
        // Add global collapse/expand controls
        this.addGlobalCollapseControls();
    }
    
    getDirectReplies(comment) {
        const commentId = comment.dataset.commentId || comment.querySelector('[data-comment-id]')?.dataset.commentId;
        if (!commentId) return [];
        
        // Find all replies that are direct children of this comment
        const allReplies = document.querySelectorAll(`.comment-item[data-parent-id="${commentId}"]`);
        return Array.from(allReplies);
    }
    
    addCollapseControl(comment, replyCount) {
        // Check if collapse control already exists
        if (comment.querySelector('.collapse-btn')) return;
        
        // Create collapse control HTML
        const collapseControl = document.createElement('div');
        collapseControl.className = 'comment-collapse-controls';
        collapseControl.innerHTML = `
            <div class="collapse-line" data-depth="0"></div>
            <button class="collapse-btn" data-comment-id="${comment.dataset.commentId}" title="Collapse/Expand thread">
                <i class="fas fa-minus"></i>
            </button>
            <div class="collapse-summary" style="display: none;">
                <i class="fas fa-comments"></i>
                <span>${replyCount} ${replyCount === 1 ? 'reply' : 'replies'} hidden</span>
                <small>- Click to expand</small>
            </div>
        `;
        
        // Insert before the comment content
        const cardBody = comment.querySelector('.card-body');
        if (cardBody) {
            cardBody.insertBefore(collapseControl, cardBody.firstChild);
        }
    }
    
    handleCollapseToggle(btn, isInitialLoad = false) {
        const commentId = btn.dataset.commentId;
        const comment = btn.closest('.comment-item');
        const collapseBtn = btn;
        const collapseSummary = comment.querySelector('.collapse-summary');
        
        console.log(`🔧 Toggling collapse for comment ${commentId}`);
        
        // Get all replies for this comment (including nested ones)
        const allReplies = this.getAllRepliesRecursive(commentId);
        
        if (collapseBtn.classList.contains('collapsed')) {
            // Expand
            console.log(`📖 Expanding ${allReplies.length} replies`);
            
            allReplies.forEach(reply => {
                reply.style.display = '';
                reply.classList.remove('collapsed');
            });
            
            collapseBtn.classList.remove('collapsed');
            collapseBtn.querySelector('i').className = 'fas fa-minus';
            collapseBtn.title = 'Collapse thread';
            
            if (collapseSummary) {
                collapseSummary.style.display = 'none';
            }
            
            // Animate expansion
            allReplies.forEach((reply, index) => {
                reply.style.opacity = '0';
                reply.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    reply.style.transition = 'all 0.3s ease';
                    reply.style.opacity = '1';
                    reply.style.transform = 'translateY(0)';
                }, index * 50);
            });
            
        } else {
            // Collapse
            console.log(`📁 Collapsing ${allReplies.length} replies`);
            
            if (isInitialLoad) {
                // Instant collapse on initial load
                allReplies.forEach(reply => {
                    reply.style.display = 'none';
                    reply.classList.add('collapsed');
                });
                
                collapseBtn.classList.add('collapsed');
                collapseBtn.querySelector('i').className = 'fas fa-plus';
                collapseBtn.title = 'Expand thread';
                
                if (collapseSummary) {
                    collapseSummary.style.display = 'flex';
                    collapseSummary.style.opacity = '1';
                    collapseSummary.style.transform = 'translateY(0)';
                }
            } else {
                // Animate collapse on user interaction
                allReplies.forEach((reply, index) => {
                    setTimeout(() => {
                        reply.style.transition = 'all 0.3s ease';
                        reply.style.opacity = '0';
                        reply.style.transform = 'translateY(-10px)';
                        
                        setTimeout(() => {
                            reply.style.display = 'none';
                            reply.classList.add('collapsed');
                        }, 300);
                    }, index * 25);
                });
                
                collapseBtn.classList.add('collapsed');
                collapseBtn.querySelector('i').className = 'fas fa-plus';
                collapseBtn.title = 'Expand thread';
                
                if (collapseSummary) {
                    setTimeout(() => {
                        collapseSummary.style.display = 'flex';
                        collapseSummary.style.opacity = '0';
                        collapseSummary.style.transform = 'translateY(-5px)';
                        
                        setTimeout(() => {
                            collapseSummary.style.transition = 'all 0.3s ease';
                            collapseSummary.style.opacity = '1';
                            collapseSummary.style.transform = 'translateY(0)';
                        }, 50);
                    }, 200);
                }
            }
        }
        
        // Update summary count
        if (collapseSummary) {
            const replyCount = allReplies.length;
            const countSpan = collapseSummary.querySelector('span');
            if (countSpan) {
                countSpan.textContent = `${replyCount} ${replyCount === 1 ? 'reply' : 'replies'} hidden`;
            }
        }
        
        // Visual feedback (only for user interactions)
        if (!isInitialLoad) {
            this.showNotification(
                collapseBtn.classList.contains('collapsed') ? 'Thread collapsed' : 'Thread expanded', 
                'info'
            );
        }
    }
    
    getAllRepliesRecursive(commentId) {
        const replies = [];
        
        // Find direct replies
        const directReplies = document.querySelectorAll(`.comment-item[data-parent-id="${commentId}"]`);
        
        directReplies.forEach(reply => {
            replies.push(reply);
            
            // Find nested replies recursively
            const replyId = reply.dataset.commentId || reply.querySelector('[data-comment-id]')?.dataset.commentId;
            if (replyId) {
                const nestedReplies = this.getAllRepliesRecursive(replyId);
                replies.push(...nestedReplies);
            }
        });
        
        return replies;
    }
    
    // Handle collapse summary click to expand
    handleCollapseSummaryClick(summary) {
        const collapseBtn = summary.closest('.comment-item').querySelector('.collapse-btn');
        if (collapseBtn) {
            this.handleCollapseToggle(collapseBtn);
        }
    }
    
    // Add global collapse/expand controls
    addGlobalCollapseControls() {
        const commentsSection = document.querySelector('.comments-section');
        if (!commentsSection) return;
        
        // Check if controls already exist
        if (commentsSection.querySelector('.global-collapse-controls')) return;
        
        // Create global controls
        const globalControls = document.createElement('div');
        globalControls.className = 'global-collapse-controls';
        globalControls.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div class="comment-count">
                    <h5 class="mb-0">
                        <i class="fas fa-comments me-2"></i>
                        <span id="visible-comment-count">${document.querySelectorAll('.comment-item').length}</span> Comments
                    </h5>
                </div>
                <div class="collapse-controls-group">
                    <button class="btn btn-sm btn-outline-secondary me-2" id="expand-all-btn">
                        <i class="fas fa-expand-alt me-1"></i>Expand All
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" id="collapse-all-btn">
                        <i class="fas fa-compress-alt me-1"></i>Collapse All
                    </button>
                </div>
            </div>
        `;
        
        // Insert before comments container
        const container = commentsSection.querySelector('.comments-container');
        if (container) {
            commentsSection.insertBefore(globalControls, container);
        }
        
        // Bind events
        document.getElementById('expand-all-btn')?.addEventListener('click', () => {
            this.handleExpandAll();
        });
        
        document.getElementById('collapse-all-btn')?.addEventListener('click', () => {
            this.handleCollapseAll();
        });
    }
    
    // Handle expand all threads
    handleExpandAll() {
        console.log('📖 Expanding all threads...');
        const collapsedBtns = document.querySelectorAll('.collapse-btn.collapsed');
        
        collapsedBtns.forEach((btn, index) => {
            setTimeout(() => {
                this.handleCollapseToggle(btn);
            }, index * 50); // Stagger for smooth animation
        });
        
        if (collapsedBtns.length > 0) {
            this.showNotification(`Expanded ${collapsedBtns.length} threads`, 'success');
        } else {
            this.showNotification('All threads are already expanded', 'info');
        }
    }
    
    // Handle collapse all threads
    handleCollapseAll() {
        console.log('📁 Collapsing all threads...');
        const expandedBtns = document.querySelectorAll('.collapse-btn:not(.collapsed)');
        
        expandedBtns.forEach((btn, index) => {
            setTimeout(() => {
                this.handleCollapseToggle(btn);
            }, index * 50); // Stagger for smooth animation
        });
        
        if (expandedBtns.length > 0) {
            this.showNotification(`Collapsed ${expandedBtns.length} threads`, 'success');
        } else {
            this.showNotification('All threads are already collapsed', 'info');
        }
    }

    async promptUserInfo(action) {
        const name = prompt(`Enter your name to ${action}:`);
        if (!name) return null;
        
        const email = prompt('Enter your email:');
        if (!email || !this.isValidEmail(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return null;
        }
        
        return { name: name.trim(), email: email.trim() };
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    debugInfo() {
        console.group('🔍 BlogCommentsSystem Debug Info');
        console.log('CSRF Token:', this.csrfToken ? '✅ Present' : '❌ Missing');
        console.log('User Session:', this.userSession);
        console.log('Liked Comments:', this.userSession.likedComments);
        
        // Check for required elements
        const elements = {
            'Comment Form': document.getElementById('commentForm'),
            'Report Modal': document.getElementById('reportModal'),
            'Report Form': document.getElementById('reportForm'),
            'Comments Container': document.querySelector('.comments-container'),
            'Sort Buttons': document.querySelectorAll('[data-sort]').length,
            'Like Buttons': document.querySelectorAll('.like-btn').length,
            'Reply Buttons': document.querySelectorAll('.reply-btn').length,
            'Share Buttons': document.querySelectorAll('.share-btn').length,
            'Report Buttons': document.querySelectorAll('.report-comment').length
        };
        
        console.log('Elements Found:');
        Object.entries(elements).forEach(([name, element]) => {
            if (element && (typeof element === 'number' ? element > 0 : true)) {
                console.log(`  ${name}: ✅`, element);
            } else {
                console.log(`  ${name}: ❌ Not found`);
            }
        });
        
        console.groupEnd();
    }
    
    showNotification(message, type = 'info') {
        // Create notification container if it doesn't exist
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        const icon = type === 'error' ? 'exclamation-circle' : 
                     type === 'success' ? 'check-circle' : 
                     type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        notification.className = 'notification-toast';
        notification.innerHTML = `
            <div class="notification-content notification-${type}">
                <i class="fas fa-${icon} notification-icon"></i>
                <div class="notification-text">${message}</div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        if (!document.getElementById('notification-styles')) {
            style.id = 'notification-styles';
            style.textContent = `
                .notification-toast {
                    margin-bottom: 10px;
                    animation: slideInRight 0.3s ease-out;
                }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 16px 20px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-left: 4px solid;
                    position: relative;
                }
                .notification-success { border-left-color: #48bb78; }
                .notification-error { border-left-color: #f56565; }
                .notification-warning { border-left-color: #ed8936; }
                .notification-info { border-left-color: #4299e1; }
                .notification-icon {
                    font-size: 20px;
                }
                .notification-success .notification-icon { color: #48bb78; }
                .notification-error .notification-icon { color: #f56565; }
                .notification-warning .notification-icon { color: #ed8936; }
                .notification-info .notification-icon { color: #4299e1; }
                .notification-text {
                    flex: 1;
                    font-size: 14px;
                    color: #2d3748;
                }
                .notification-close {
                    background: none;
                    border: none;
                    color: #a0aec0;
                    cursor: pointer;
                    padding: 4px;
                    margin-left: 8px;
                }
                .notification-close:hover {
                    color: #718096;
                }
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    /**
     * Check content for profanity
     * @param {string} content - Content to check
     * @returns {object} - Results with hasProfanity, severity, foundWords
     */
    checkProfanity(content) {
        if (!content) return { hasProfanity: false, severity: 'none', foundWords: [] };

        const contentLower = content.toLowerCase();
        const foundWords = [];

        // Basic word check
        const words = contentLower.match(/\b\w+\b/g) || [];
        words.forEach(word => {
            if (this.profanityWords.includes(word)) {
                foundWords.push(word);
            }
        });

        // Advanced detection for circumvention
        foundWords.push(...this.detectAdvancedProfanity(contentLower));

        // Remove duplicates
        const uniqueWords = [...new Set(foundWords)];

        // Determine severity based on refined categories
        let severity = 'none';
        if (uniqueWords.length > 0) {
            // Severe: Racist, extremely vulgar, hate speech
            const severeWords = ['nigger', 'faggot', 'motherfucker', 'cunt', 'bougnoule', 'nègre', 'bicot', 'raton', 'chintok', 'youpin', 'feuj', 'kanker'];
            
            // Moderate: Strong insults and vulgar terms
            const moderateWords = ['fuck', 'shit', 'bitch', 'connard', 'salope', 'pute', 'enculé', 'pédé', 'tapette', 'gilipollas'];

            if (uniqueWords.some(word => severeWords.includes(word))) {
                severity = 'severe';
            } else if (uniqueWords.some(word => moderateWords.includes(word))) {
                severity = 'moderate';
            } else {
                severity = 'mild';
            }
        }

        return {
            hasProfanity: uniqueWords.length > 0,
            severity: severity,
            foundWords: uniqueWords
        };
    }

    detectAdvancedProfanity(text) {
        const found = [];

        // Remove special characters and numbers, check again
        const cleanText = text.replace(/[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]/g, '');
        this.profanityWords.forEach(word => {
            const cleanWord = word.replace(/[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]/g, '');
            if (cleanText.includes(cleanWord)) {
                found.push(word);
            }
        });

        // Check for leetspeak and substitutions
        let normalizedText = text;
        const substitutions = {
            '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '9': 'g',
            '@': 'a', '$': 's', '!': 'i', '*': '', '-': '', '_': '', '.': ''
        };

        Object.keys(substitutions).forEach(symbol => {
            normalizedText = normalizedText.replaceAll(symbol, substitutions[symbol]);
        });

        const normalizedWords = normalizedText.match(/\b\w+\b/g) || [];
        normalizedWords.forEach(word => {
            if (this.profanityWords.includes(word)) {
                found.push(word);
            }
        });

        // Check for spaced words (e.g., "p u t a i n")
        const spacedPattern = text.replace(/\s+/g, '');
        this.profanityWords.forEach(word => {
            if (spacedPattern.includes(word)) {
                found.push(word);
            }
        });

        // Phonetic variations
        const phoneticMap = {
            'putin': 'putain', 'poutain': 'putain', 'putein': 'putain',
            'mrd': 'merde', 'mrde': 'merde', 'mer2': 'merde',
            'conar': 'connard', 'konar': 'connard',
            'salop': 'salope', 'encule': 'enculé',
            'fuk': 'fuck', 'fok': 'fuck', 'phuck': 'fuck',
            'sht': 'shit', 'chit': 'shit', 'shyt': 'shit',
            'biatch': 'bitch', 'bytch': 'bitch'
        };

        const textWords = text.match(/\b\w+\b/g) || [];
        textWords.forEach(word => {
            if (phoneticMap[word]) {
                found.push(phoneticMap[word]);
            }
        });

        return found;
    }

    // Note: Profanity warnings are now handled server-side only for better UX
}

// Prevent extension interference
window.addEventListener('error', function(e) {
    // Suppress extension-related errors that don't affect our functionality
    if (e.message && (
        e.message.includes('Extension context invalidated') ||
        e.message.includes('message channel closed') ||
        e.message.includes('listener indicated an asynchronous response') ||
        e.message.includes('chrome-extension://') ||
        e.filename && e.filename.includes('chrome-extension://')
    )) {
        console.debug('🛡️ Extension error suppressed:', e.message);
        e.preventDefault();
        return false;
    }
});

// Prevent unhandled promise rejections from extensions
window.addEventListener('unhandledrejection', function(e) {
    if (e.reason && typeof e.reason === 'string' && (
        e.reason.includes('Extension context invalidated') ||
        e.reason.includes('message channel closed') ||
        e.reason.includes('chrome-extension://')
    )) {
        console.debug('🛡️ Extension promise rejection suppressed:', e.reason);
        e.preventDefault();
        return false;
    }
});

// Initialize the comments system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, initializing BlogCommentsSystem...');
    
    // Check dependencies
    if (typeof bootstrap === 'undefined') {
        console.warn('⚠️ Bootstrap is not loaded. Some features may not work properly.');
    } else {
        console.log('✅ Bootstrap detected');
    }
    
    // Check for Font Awesome
    const iconTest = document.querySelector('.fas');
    if (!iconTest) {
        console.warn('⚠️ No Font Awesome icons found. Icons may not display properly.');
    } else {
        console.log('✅ Font Awesome icons detected');
    }
    
    // Initialize the system with error handling
    try {
        window.blogCommentsSystem = new BlogCommentsSystem();
        console.log('✅ BlogCommentsSystem initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize BlogCommentsSystem:', error);
        
        // Retry initialization after a delay if it failed due to extension interference
        if (error.message && error.message.includes('Extension')) {
            console.log('🔄 Retrying initialization in 1 second...');
            setTimeout(() => {
                try {
                    window.blogCommentsSystem = new BlogCommentsSystem();
                    console.log('✅ BlogCommentsSystem initialized successfully on retry');
                } catch (retryError) {
                    console.error('❌ Retry failed:', retryError);
                }
            }, 1000);
        }
    }
});

// Export for potential external use
window.BlogCommentsSystem = BlogCommentsSystem;