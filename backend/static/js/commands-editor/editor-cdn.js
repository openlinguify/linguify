/**
 * Linguify Editor.js CDN Loader
 * Dynamically loads all required Editor.js dependencies
 */

class EditorJSLoader {
    constructor() {
        this.scripts = [
            // Core
            'https://unpkg.com/@editorjs/editorjs@2.29.1/dist/editorjs.umd.min.js',
            
            // Tools
            'https://unpkg.com/@editorjs/header@2.8.1/dist/header.umd.min.js',
            'https://unpkg.com/@editorjs/paragraph@2.11.6/dist/paragraph.umd.min.js',
            'https://unpkg.com/@editorjs/list@1.9.0/dist/list.umd.min.js',
            'https://unpkg.com/@editorjs/quote@2.6.0/dist/quote.umd.min.js',
            'https://unpkg.com/@editorjs/code@2.9.0/dist/code.umd.min.js',
            'https://unpkg.com/@editorjs/delimiter@1.4.2/dist/delimiter.umd.min.js',
            'https://unpkg.com/@editorjs/table@2.4.1/dist/table.umd.min.js',
            'https://unpkg.com/@editorjs/checklist@1.6.0/dist/checklist.umd.min.js',
            'https://unpkg.com/@editorjs/link@2.6.2/dist/link.umd.min.js',
            'https://unpkg.com/@editorjs/image@2.9.3/dist/image.umd.min.js',
            
            // Inline Tools
            'https://unpkg.com/@editorjs/marker@1.4.0/dist/marker.umd.min.js',
            'https://unpkg.com/@editorjs/inline-code@1.5.1/dist/inline-code.umd.min.js',
            
            // Custom Tools (skip this for now as it might be causing issues)
            // 'https://unpkg.com/editorjs-alert@latest/dist/alert.umd.js'
        ];
        
        // Fallback CDN
        this.fallbackScripts = [
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
            'https://cdn.jsdelivr.net/npm/@editorjs/inline-code@1.5.1/dist/inline-code.umd.min.js'
        ];
        
        this.loaded = false;
        this.callbacks = [];
        this.usedFallback = false;
    }
    
    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                console.log(`✅ Script already loaded: ${src}`);
                resolve();
                return;
            }
            
            console.log(`📦 Loading script: ${src}`);
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                console.log(`✅ Successfully loaded: ${src}`);
                resolve();
            };
            script.onerror = (error) => {
                console.error(`❌ Failed to load script: ${src}`, error);
                reject(new Error(`Failed to load ${src}`));
            };
            document.head.appendChild(script);
        });
    }
    
    async loadAll() {
        if (this.loaded) {
            console.log('📚 Editor.js dependencies already loaded');
            return Promise.resolve();
        }
        
        console.log('📦 Starting to load Editor.js dependencies...');
        
        try {
            await this.tryLoadScripts(this.scripts, 'primary CDN (unpkg)');
        } catch (primaryError) {
            console.warn('⚠️ Primary CDN failed, trying fallback CDN...', primaryError);
            try {
                this.usedFallback = true;
                await this.tryLoadScripts(this.fallbackScripts, 'fallback CDN (jsdelivr)');
            } catch (fallbackError) {
                console.error('💥 Both CDNs failed!', fallbackError);
                throw new Error('All CDN sources failed to load Editor.js dependencies');
            }
        }
        
        return Promise.resolve();
    }
    
    async tryLoadScripts(scripts, source) {
        console.log(`🎯 Loading from ${source}...`);
        
        // Load core EditorJS first
        console.log('🎯 Loading core EditorJS...');
        await this.loadScript(scripts[0]);
        
        // Wait a bit for EditorJS to initialize
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Check if EditorJS is available
        if (typeof window.EditorJS === 'undefined') {
            throw new Error('EditorJS core failed to load properly');
        }
        console.log('✅ EditorJS core loaded successfully');
        
        // Load remaining scripts (tools) with some delay between each
        console.log('🔧 Loading Editor.js tools...');
        for (let i = 1; i < scripts.length; i++) {
            try {
                await this.loadScript(scripts[i]);
                // Small delay between tool loads
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (toolError) {
                console.warn(`⚠️ Failed to load tool: ${scripts[i]}`, toolError);
                // Continue with other tools even if one fails
            }
        }
        
        this.loaded = true;
        console.log(`🎉 Editor.js dependencies loaded successfully from ${source}!`);
        
        // Execute callbacks
        this.callbacks.forEach(callback => callback());
        this.callbacks = [];
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