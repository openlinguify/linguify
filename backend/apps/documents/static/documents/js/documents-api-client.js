/**
 * Documents API Client with Enhanced Error Handling
 * Provides a robust interface to the Documents API with comprehensive error handling
 */

class DocumentsAPIClient {
    constructor() {
        this.baseUrl = '/documents/api/v1/';
        this.errorHandler = window.DocumentsErrorHandler;
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
        
        // Request cache for optimistic UI updates
        this.requestCache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }
    
    /**
     * Make API request with error handling and retries
     */
    async request(endpoint, options = {}) {
        const cacheKey = this.getCacheKey(endpoint, options);
        
        // Check cache for GET requests
        if ((!options.method || options.method === 'GET') && this.requestCache.has(cacheKey)) {
            const cached = this.requestCache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }
        
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const data = await this.errorHandler.apiRequest(endpoint, options);
                
                // Cache successful GET requests
                if (!options.method || options.method === 'GET') {
                    this.requestCache.set(cacheKey, {
                        data: data,
                        timestamp: Date.now()
                    });
                }
                
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry for client errors (4xx) except 429 (rate limit)
                if (error.status >= 400 && error.status < 500 && error.status !== 429) {
                    break;
                }
                
                // Wait before retry
                if (attempt < this.retryAttempts) {
                    await this.delay(this.retryDelay * attempt);
                }
            }
        }
        
        throw lastError;
    }
    
    /**
     * Documents API methods
     */
    
    // Document operations
    async getDocuments(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `documents/${queryString ? '?' + queryString : ''}`;
        return await this.request(endpoint);
    }
    
    async getDocument(id) {
        return await this.request(`documents/${id}/`);
    }
    
    async createDocument(data) {
        this.invalidateCache('documents');
        return await this.request('documents/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async updateDocument(id, data) {
        this.invalidateCache(`documents/${id}`);
        this.invalidateCache('documents');
        return await this.request(`documents/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    async deleteDocument(id) {
        this.invalidateCache(`documents/${id}`);
        this.invalidateCache('documents');
        return await this.request(`documents/${id}/`, {
            method: 'DELETE'
        });
    }
    
    async duplicateDocument(id) {
        this.invalidateCache('documents');
        return await this.request(`documents/${id}/duplicate/`, {
            method: 'POST'
        });
    }
    
    async exportDocument(id, format = 'markdown') {
        return await this.request(`documents/${id}/export/?format=${format}`);
    }
    
    // Folder operations
    async getFolders() {
        return await this.request('folders/');
    }
    
    async getFolder(id) {
        return await this.request(`folders/${id}/`);
    }
    
    async createFolder(data) {
        this.invalidateCache('folders');
        return await this.request('folders/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async updateFolder(id, data) {
        this.invalidateCache(`folders/${id}`);
        this.invalidateCache('folders');
        return await this.request(`folders/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    async deleteFolder(id) {
        this.invalidateCache(`folders/${id}`);
        this.invalidateCache('folders');
        return await this.request(`folders/${id}/`, {
            method: 'DELETE'
        });
    }
    
    async getFolderDocuments(id) {
        return await this.request(`folders/${id}/documents/`);
    }
    
    // Document sharing operations
    async getShares() {
        return await this.request('shares/');
    }
    
    async createShare(data) {
        this.invalidateCache('shares');
        return await this.request('shares/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async updateShare(id, data) {
        this.invalidateCache(`shares/${id}`);
        this.invalidateCache('shares');
        return await this.request(`shares/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    async deleteShare(id) {
        this.invalidateCache(`shares/${id}`);
        this.invalidateCache('shares');
        return await this.request(`shares/${id}/`, {
            method: 'DELETE'
        });
    }
    
    // Document versions
    async getVersions(documentId) {
        return await this.request(`versions/?document=${documentId}`);
    }
    
    async getVersion(id) {
        return await this.request(`versions/${id}/`);
    }
    
    async restoreVersion(id) {
        this.invalidateCache('documents');
        return await this.request(`versions/${id}/restore/`, {
            method: 'POST'
        });
    }
    
    // Document comments
    async getComments(documentId) {
        return await this.request(`comments/?document=${documentId}`);
    }
    
    async createComment(data) {
        this.invalidateCache('comments');
        return await this.request('comments/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async updateComment(id, data) {
        this.invalidateCache(`comments/${id}`);
        this.invalidateCache('comments');
        return await this.request(`comments/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    async deleteComment(id) {
        this.invalidateCache(`comments/${id}`);
        this.invalidateCache('comments');
        return await this.request(`comments/${id}/`, {
            method: 'DELETE'
        });
    }
    
    async resolveComment(id) {
        this.invalidateCache(`comments/${id}`);
        return await this.request(`comments/${id}/resolve/`, {
            method: 'POST'
        });
    }
    
    async unresolveComment(id) {
        this.invalidateCache(`comments/${id}`);
        return await this.request(`comments/${id}/unresolve/`, {
            method: 'POST'
        });
    }
    
    /**
     * Utility methods
     */
    
    getCacheKey(endpoint, options) {
        return `${options.method || 'GET'}:${endpoint}:${JSON.stringify(options.body || {})}`;
    }
    
    invalidateCache(pattern) {
        for (const [key] of this.requestCache) {
            if (key.includes(pattern)) {
                this.requestCache.delete(key);
            }
        }
    }
    
    clearCache() {
        this.requestCache.clear();
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Optimistic UI helper methods
     */
    
    async optimisticCreate(collection, data, createFn) {
        // Optimistically add to UI
        const tempId = 'temp_' + Date.now();
        const optimisticItem = { ...data, id: tempId, _optimistic: true };
        
        try {
            // Dispatch optimistic update event
            document.dispatchEvent(new CustomEvent('documents:optimistic-create', {
                detail: { collection, item: optimisticItem }
            }));
            
            // Perform actual API call
            const result = await createFn(data);
            
            // Dispatch success event
            document.dispatchEvent(new CustomEvent('documents:create-success', {
                detail: { collection, tempId, item: result }
            }));
            
            return result;
            
        } catch (error) {
            // Dispatch error event
            document.dispatchEvent(new CustomEvent('documents:create-error', {
                detail: { collection, tempId, error }
            }));
            
            throw error;
        }
    }
    
    async optimisticUpdate(collection, id, data, updateFn) {
        // Dispatch optimistic update event
        document.dispatchEvent(new CustomEvent('documents:optimistic-update', {
            detail: { collection, id, data }
        }));
        
        try {
            const result = await updateFn(id, data);
            
            // Dispatch success event
            document.dispatchEvent(new CustomEvent('documents:update-success', {
                detail: { collection, id, item: result }
            }));
            
            return result;
            
        } catch (error) {
            // Dispatch error event to revert optimistic update
            document.dispatchEvent(new CustomEvent('documents:update-error', {
                detail: { collection, id, error }
            }));
            
            throw error;
        }
    }
    
    async optimisticDelete(collection, id, deleteFn) {
        // Dispatch optimistic delete event
        document.dispatchEvent(new CustomEvent('documents:optimistic-delete', {
            detail: { collection, id }
        }));
        
        try {
            await deleteFn(id);
            
            // Dispatch success event
            document.dispatchEvent(new CustomEvent('documents:delete-success', {
                detail: { collection, id }
            }));
            
        } catch (error) {
            // Dispatch error event to restore item
            document.dispatchEvent(new CustomEvent('documents:delete-error', {
                detail: { collection, id, error }
            }));
            
            throw error;
        }
    }
    
    /**
     * Real-time updates simulation (can be replaced with WebSocket)
     */
    
    startPolling(endpoint, interval = 30000) {
        const pollId = setInterval(async () => {
            try {
                const data = await this.request(endpoint);
                document.dispatchEvent(new CustomEvent('documents:data-update', {
                    detail: { endpoint, data }
                }));
            } catch (error) {
                this.errorHandler.logError({
                    type: 'polling_error',
                    endpoint: endpoint,
                    error: error.message
                });
            }
        }, interval);
        
        return pollId;
    }
    
    stopPolling(pollId) {
        clearInterval(pollId);
    }
}

// Global instance
window.documentsAPI = new DocumentsAPIClient();

// Helper functions for common operations
window.documentsHelpers = {
    
    // Show loading state
    showLoading(element, message = 'Chargement...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        element.style.position = 'relative';
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">${message}</span>
                </div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        element.appendChild(loader);
    },
    
    // Hide loading state
    hideLoading(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        const loader = element.querySelector('.loading-overlay');
        if (loader) {
            loader.remove();
        }
    },
    
    // Show success message
    showSuccess(message, duration = 3000) {
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="bi bi-check-circle"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    },
    
    // Show error message
    showError(message, error = null) {
        console.error('API Error:', error);
        
        let errorMessage = message;
        if (error && error.data && error.data.message) {
            errorMessage += ': ' + error.data.message;
        }
        
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle"></i>
                ${errorMessage}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 8081);
    },
    
    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Add CSS for loading overlays and notifications
const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .loading-content {
        text-align: center;
        color: #6c757d;
    }
    
    .loading-text {
        margin-top: 0.5rem;
        font-size: 0.875rem;
    }
    
    .success-notification,
    .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
    }
`;
document.head.appendChild(style);

console.log('📡 Documents API Client loaded with enhanced error handling');