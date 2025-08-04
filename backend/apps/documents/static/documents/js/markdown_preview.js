/**
 * Markdown Preview Utility
 * Converts markdown text to HTML for live preview
 */

class MarkdownPreview {
    constructor() {
        this.rules = [
            // Headers
            { regex: /^### (.*$)/gim, replacement: '<h3>$1</h3>' },
            { regex: /^## (.*$)/gim, replacement: '<h2>$1</h2>' },
            { regex: /^# (.*$)/gim, replacement: '<h1>$1</h1>' },
            
            // Emphasis
            { regex: /\*\*(.*?)\*\*/gim, replacement: '<strong>$1</strong>' },
            { regex: /\*(.*?)\*/gim, replacement: '<em>$1</em>' },
            { regex: /~~(.*?)~~/gim, replacement: '<del>$1</del>' },
            
            // Code
            { regex: /```([\s\S]*?)```/gim, replacement: '<pre><code>$1</code></pre>' },
            { regex: /`(.*?)`/gim, replacement: '<code>$1</code>' },
            
            // Links
            { regex: /\[([^\]]+)\]\(([^\)]+)\)/gim, replacement: '<a href="$2">$1</a>' },
            { regex: /(https?:\/\/[^\s]+)/gim, replacement: '<a href="$1">$1</a>' },
            
            // Images
            { regex: /!\[([^\]]*)\]\(([^\)]+)\)/gim, replacement: '<img src="$2" alt="$1" class="img-fluid">' },
            
            // Lists
            { regex: /^\* (.+$)/gim, replacement: '<li>$1</li>' },
            { regex: /^- (.+$)/gim, replacement: '<li>$1</li>' },
            { regex: /^\+ (.+$)/gim, replacement: '<li>$1</li>' },
            
            // Ordered lists
            { regex: /^\d+\. (.+$)/gim, replacement: '<li>$1</li>' },
            
            // Blockquotes
            { regex: /^> (.+$)/gim, replacement: '<blockquote>$1</blockquote>' },
            
            // Horizontal rules
            { regex: /^---$/gim, replacement: '<hr>' },
            { regex: /^\*\*\*$/gim, replacement: '<hr>' },
            
            // Line breaks
            { regex: /\n\n/gim, replacement: '</p><p>' },
            { regex: /\n/gim, replacement: '<br>' }
        ];
    }
    
    /**
     * Convert markdown text to HTML
     * @param {string} markdown - The markdown text to convert
     * @returns {string} - The converted HTML
     */
    toHtml(markdown) {
        if (!markdown) return '';
        
        let html = markdown;
        
        // Apply all conversion rules
        this.rules.forEach(rule => {
            html = html.replace(rule.regex, rule.replacement);
        });
        
        // Post-process lists
        html = this.processLists(html);
        
        // Wrap in paragraphs
        html = this.wrapParagraphs(html);
        
        // Clean up
        html = this.cleanup(html);
        
        return html;
    }
    
    /**
     * Process list items and wrap them in proper list tags
     * @param {string} html - HTML with list items
     * @returns {string} - HTML with proper list structure
     */
    processLists(html) {
        // Wrap consecutive <li> elements in <ul>
        html = html.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gims, (match) => {
            return '<ul>' + match + '</ul>';
        });
        
        // Handle ordered lists (basic implementation)
        html = html.replace(/(<li>\d+\. .*?<\/li>)(\s*<li>\d+\. .*?<\/li>)*/gims, (match) => {
            const cleanedMatch = match.replace(/\d+\. /g, '');
            return '<ol>' + cleanedMatch + '</ol>';
        });
        
        return html;
    }
    
    /**
     * Wrap content in paragraph tags
     * @param {string} html - HTML content
     * @returns {string} - HTML wrapped in paragraphs
     */
    wrapParagraphs(html) {
        // Split by double line breaks and wrap in paragraphs
        const parts = html.split('</p><p>');
        
        if (parts.length > 1) {
            return '<p>' + parts.join('</p><p>') + '</p>';
        }
        
        // If no double line breaks, wrap everything in a paragraph
        // unless it starts with a block element
        if (!html.match(/^<(h[1-6]|ul|ol|blockquote|pre|hr)/)) {
            return '<p>' + html + '</p>';
        }
        
        return html;
    }
    
    /**
     * Clean up the generated HTML
     * @param {string} html - HTML to clean up
     * @returns {string} - Cleaned HTML
     */
    cleanup(html) {
        return html
            // Remove empty paragraphs
            .replace(/<p>\s*<\/p>/gim, '')
            // Remove paragraphs around block elements
            .replace(/<p>\s*(<(h[1-6]|ul|ol|blockquote|pre|hr)[^>]*>.*?<\/\2>)\s*<\/p>/gims, '$1')
            // Fix nested emphasis
            .replace(/<(strong|em)>\s*<\/\1>/gim, '')
            // Trim whitespace
            .trim();
    }
    
    /**
     * Extract plain text from markdown (for search, etc.)
     * @param {string} markdown - The markdown text
     * @returns {string} - Plain text version
     */
    toPlainText(markdown) {
        if (!markdown) return '';
        
        return markdown
            // Remove code blocks
            .replace(/```[\s\S]*?```/gim, '')
            // Remove inline code
            .replace(/`.*?`/gim, '')
            // Remove images
            .replace(/!\[.*?\]\(.*?\)/gim, '')
            // Remove links but keep text
            .replace(/\[([^\]]+)\]\([^\)]+\)/gim, '$1')
            // Remove emphasis markers
            .replace(/\*\*(.*?)\*\*/gim, '$1')
            .replace(/\*(.*?)\*/gim, '$1')
            .replace(/~~(.*?)~~/gim, '$1')
            // Remove headers
            .replace(/^#{1,6}\s+/gim, '')
            // Remove lists
            .replace(/^[\*\-\+]\s+/gim, '')
            .replace(/^\d+\.\s+/gim, '')
            // Remove blockquotes
            .replace(/^>\s+/gim, '')
            // Clean up whitespace
            .replace(/\n+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    /**
     * Get word count from markdown
     * @param {string} markdown - The markdown text
     * @returns {number} - Word count
     */
    getWordCount(markdown) {
        const plainText = this.toPlainText(markdown);
        return plainText ? plainText.split(/\s+/).length : 0;
    }
    
    /**
     * Get reading time estimate
     * @param {string} markdown - The markdown text
     * @returns {number} - Estimated reading time in minutes
     */
    getReadingTime(markdown) {
        const wordCount = this.getWordCount(markdown);
        const wordsPerMinute = 200; // Average reading speed
        return Math.ceil(wordCount / wordsPerMinute);
    }
    
    /**
     * Extract headings from markdown for table of contents
     * @param {string} markdown - The markdown text
     * @returns {Array} - Array of heading objects
     */
    getHeadings(markdown) {
        if (!markdown) return [];
        
        const headings = [];
        const lines = markdown.split('\n');
        
        lines.forEach((line, index) => {
            const match = line.match(/^(#{1,6})\s+(.+)$/);
            if (match) {
                const level = match[1].length;
                const text = match[2].trim();
                const id = this.generateHeadingId(text);
                
                headings.push({
                    level,
                    text,
                    id,
                    line: index + 1
                });
            }
        });
        
        return headings;
    }
    
    /**
     * Generate a URL-friendly ID from heading text
     * @param {string} text - The heading text
     * @returns {string} - URL-friendly ID
     */
    generateHeadingId(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '') // Remove special characters
            .replace(/\s+/g, '-') // Replace spaces with hyphens
            .replace(/-+/g, '-') // Replace multiple hyphens with single
            .trim('-'); // Remove leading/trailing hyphens
    }
    
    /**
     * Add IDs to headings in HTML for anchor links
     * @param {string} html - HTML content
     * @returns {string} - HTML with heading IDs
     */
    addHeadingIds(html) {
        return html.replace(/<h([1-6])>(.*?)<\/h[1-6]>/gim, (match, level, text) => {
            const id = this.generateHeadingId(text);
            return `<h${level} id="${id}">${text}</h${level}>`;
        });
    }
}

// Create global instance
window.markdownPreview = new MarkdownPreview();

// Integrate with document editor if present
document.addEventListener('DOMContentLoaded', () => {
    const markdownTextarea = document.getElementById('markdown-content');
    const previewElement = document.getElementById('markdown-preview');
    
    if (markdownTextarea && previewElement) {
        // Initial preview
        updateMarkdownPreview();
        
        // Update on input
        markdownTextarea.addEventListener('input', updateMarkdownPreview);
        
        function updateMarkdownPreview() {
            const markdown = markdownTextarea.value;
            const html = window.markdownPreview.addHeadingIds(
                window.markdownPreview.toHtml(markdown)
            );
            previewElement.innerHTML = html;
            
            // Update word count if element exists
            const wordCountElement = document.getElementById('word-count');
            if (wordCountElement) {
                const wordCount = window.markdownPreview.getWordCount(markdown);
                const readingTime = window.markdownPreview.getReadingTime(markdown);
                wordCountElement.textContent = `${wordCount} mots • ${readingTime} min de lecture`;
            }
        }
    }
});