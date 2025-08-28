/**
 * Linguify Editor.js CDN Loader
 * Dynamically loads all required Editor.js dependencies
 */

class EditorJSLoader {
    constructor() {
        this.scripts = [
            // Core
            'https://cdn.jsdelivr.net/npm/@editorjs/editorjs@2.29.1/dist/editorjs.umd.min.js',
            
            // Tools
            'https://cdn.jsdelivr.net/npm/@editorjs/header@2.8.1/dist/header.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/paragraph@2.11.6/dist/paragraph.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/list@1.9.0/dist/list.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/quote@2.6.0/dist/quote.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/code@2.9.0/dist/code.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/delimiter@1.4.2/dist/delimiter.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/table@2.4.1/dist/table.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/checklist@1.6.0/dist/checklist.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/link@2.6.2/dist/link.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/image@2.9.3/dist/image.umd.min.js',
            
            // Inline Tools
            'https://cdn.jsdelivr.net/npm/@editorjs/marker@1.4.0/dist/marker.umd.min.js',
            'https://cdn.jsdelivr.net/npm/@editorjs/inline-code@1.5.1/dist/inline-code.umd.min.js',
            
            // Custom Tools
            'https://cdn.jsdelivr.net/npm/editorjs-alert@latest/dist/alert.umd.js'
        ];
        
        this.loaded = false;
        this.callbacks = [];
    }
    
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    async loadAll() {
        if (this.loaded) {
            return Promise.resolve();
        }
        
        try {
            // Load scripts sequentially to avoid dependency issues
            for (const src of this.scripts) {
                await this.loadScript(src);
            }
            
            this.loaded = true;
            
            // Execute callbacks
            this.callbacks.forEach(callback => callback());
            this.callbacks = [];
            
            return Promise.resolve();
        } catch (error) {
            console.error('Failed to load Editor.js dependencies:', error);
            return Promise.reject(error);
        }
    }
    
    onReady(callback) {
        if (this.loaded) {
            callback();
        } else {
            this.callbacks.push(callback);
        }
    }
    
    // Static method for easy use
    static async init() {
        const loader = new EditorJSLoader();
        await loader.loadAll();
        return loader;
    }
}

// Export for global use
window.EditorJSLoader = EditorJSLoader;