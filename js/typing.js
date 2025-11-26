// Typing animation for text elements
class TextTyper {
    constructor(element, options = {}) {
        this.element = element;
        this.texts = Array.isArray(options.text) ? options.text : [options.text];
        this.typingSpeed = options.typingSpeed || 80;
        this.deletingSpeed = options.deletingSpeed || 40;
        this.pauseDuration = options.pauseDuration || 2000;
        this.initialDelay = options.initialDelay || 0;
        this.loop = options.loop !== undefined ? options.loop : true;
        this.showCursor = options.showCursor !== undefined ? options.showCursor : true;
        this.cursorCharacter = options.cursorCharacter || '|';
        this.cursorBlinkDuration = options.cursorBlinkDuration || 500;
        
        this.currentTextIndex = 0;
        this.currentCharIndex = 0;
        this.isDeleting = false;
        this.cursorElement = null;
        
        this.init();
    }
    
    init() {
        // Create cursor element if needed
        if (this.showCursor) {
            this.cursorElement = document.createElement('span');
            this.cursorElement.className = 'typing-cursor';
            this.cursorElement.textContent = this.cursorCharacter;
            this.element.parentNode.insertBefore(this.cursorElement, this.element.nextSibling);
            
            // Blink cursor
            this.cursorInterval = setInterval(() => {
                if (this.cursorElement) {
                    this.cursorElement.style.opacity = 
                        this.cursorElement.style.opacity === '0' ? '1' : '0';
                }
            }, this.cursorBlinkDuration);
        }
        
        // Start typing after initial delay
        setTimeout(() => this.type(), this.initialDelay);
    }
    
    stopCursor() {
        if (this.cursorInterval) {
            clearInterval(this.cursorInterval);
        }
        if (this.cursorElement) {
            this.cursorElement.style.opacity = '0';
        }
    }
    
    type() {
        const currentText = this.texts[this.currentTextIndex];
        
        if (this.isDeleting) {
            // Deleting text
            if (this.currentCharIndex > 0) {
                this.currentCharIndex--;
                this.element.textContent = currentText.substring(0, this.currentCharIndex);
                setTimeout(() => this.type(), this.deletingSpeed);
            } else {
                // Finished deleting
                this.isDeleting = false;
                
                // Move to next text
                if (this.currentTextIndex < this.texts.length - 1 || this.loop) {
                    this.currentTextIndex = (this.currentTextIndex + 1) % this.texts.length;
                    setTimeout(() => this.type(), this.pauseDuration / 2);
                }
            }
        } else {
            // Typing text
            if (this.currentCharIndex < currentText.length) {
                this.currentCharIndex++;
                this.element.textContent = currentText.substring(0, this.currentCharIndex);
                
                // Variable speed for more natural effect
                const speed = this.typingSpeed + Math.random() * 50 - 25;
                setTimeout(() => this.type(), Math.max(30, speed));
            } else {
                // Finished typing
                if (this.texts.length > 1 && (this.loop || this.currentTextIndex < this.texts.length - 1)) {
                    // Wait before deleting
                    setTimeout(() => {
                        this.isDeleting = true;
                        this.type();
                    }, this.pauseDuration);
                } else {
                    // Finished all typing, stop cursor
                    this.stopCursor();
                }
            }
        }
    }
}

// Initialize typing animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const titleElement = document.getElementById('typing-title');
    const descriptionElement = document.getElementById('typing-description');
    
    if (titleElement) {
        new TextTyper(titleElement, {
            text: 'Code Graph Gallery',
            typingSpeed: 120,
            deletingSpeed: 0,
            pauseDuration: 0,
            initialDelay: 500,
            loop: false,
            showCursor: false
        });
    }
    
    if (descriptionElement) {
        new TextTyper(descriptionElement, {
            text: '这是一个用于展示各种代码图表示例的平台。点击图表即可查看详细的代码实现和说明。',
            typingSpeed: 60,
            deletingSpeed: 0,
            pauseDuration: 0,
            initialDelay: 2800,
            loop: false,
            showCursor: true,
            cursorCharacter: '|',
            cursorBlinkDuration: 530
        });
    }
});
