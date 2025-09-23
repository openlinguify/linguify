// Linguify Editor - Notebook Slash Commands and Formatting Toolbar
// This file contains the Alpine.js components for the notebook editor
// Part of the Linguify platform

// Slash commands component for the notebook editor
function notebookSlashCommands() {
    return {
        showCommands: false,
        commandPosition: { x: 0, y: 0 },
        selectedCommand: 0,
        commands: [
            { name: 'Note', text: '**Note:** ' },
            { name: 'Tâche', text: '☐ ' },
            { name: 'Idée', text: '**Idée:** ' },
            { name: 'Question', text: '**Question:** ' },
            { name: 'Traduction', text: '**FR:** \n**EN:** ' },
            { name: 'Vocabulaire', text: '**Mot:** définition' },
            { name: 'Rappel', text: '**Rappel:** ' }
        ],

        // Formatting toolbar
        showFormatToolbar: false,
        toolbarPosition: { x: 0, y: 0 },
        selectedText: '',
        selectionStart: 0,
        selectionEnd: 0,

        handleKeydown(event) {
            const textarea = event.target;

            if (event.key === '/') {
                const cursorPos = textarea.selectionStart;
                const textBefore = textarea.value.substring(0, cursorPos);

                // Only show commands if at start of line or after space
                if (cursorPos === 0 || textBefore.endsWith('\n') || textBefore.endsWith(' ')) {
                    event.preventDefault(); // Prevent the "/" from being typed
                    setTimeout(() => {
                        this.showCommandMenu(textarea);
                    }, 10);
                }
            }

            if (this.showCommands) {
                if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    this.selectedCommand = (this.selectedCommand + 1) % this.commands.length;
                } else if (event.key === 'ArrowUp') {
                    event.preventDefault();
                    this.selectedCommand = this.selectedCommand === 0 ? this.commands.length - 1 : this.selectedCommand - 1;
                } else if (event.key === 'Enter') {
                    event.preventDefault();
                    this.insertCommand(textarea);
                } else if (event.key === 'Escape' || event.key === ' ') {
                    this.hideCommandMenu();
                    if (event.key === ' ') {
                        // Allow space to be typed if escaping commands
                        textarea.value = textarea.value.substring(0, textarea.selectionStart) + ' ' + textarea.value.substring(textarea.selectionStart);
                        textarea.setSelectionRange(textarea.selectionStart + 1, textarea.selectionStart + 1);
                        textarea.dispatchEvent(new Event('input'));
                    }
                } else if (event.key.length === 1) {
                    // Hide menu if user starts typing normal text
                    this.hideCommandMenu();
                }
            }
        },

        showCommandMenu(textarea) {
            const cursorPos = textarea.selectionStart;
            const textBeforeCursor = textarea.value.substring(0, cursorPos);
            const lines = textBeforeCursor.split('\n');
            const currentLine = lines.length - 1;
            const currentColumn = lines[lines.length - 1].length;

            // Get textarea styles for accurate positioning
            const style = window.getComputedStyle(textarea);
            const lineHeight = parseInt(style.lineHeight) || 24;
            const fontSize = parseInt(style.fontSize) || 16;
            const paddingTop = parseInt(style.paddingTop) || 0;
            const paddingLeft = parseInt(style.paddingLeft) || 0;

            // Calculate approximate character width
            const charWidth = fontSize * 0.6; // Rough estimate for monospace-ish fonts

            // Get textarea position
            const rect = textarea.getBoundingClientRect();

            // Calculate cursor position
            const cursorX = rect.left + paddingLeft + (currentColumn * charWidth);
            const cursorY = rect.top + paddingTop + (currentLine * lineHeight);

            // Menu dimensions (approximate)
            const menuHeight = 250; // Approximate height of the commands menu
            const menuWidth = 220;

            // Check if there's enough space below the cursor
            const spaceBelow = window.innerHeight - (cursorY + lineHeight);
            const spaceAbove = cursorY - rect.top;

            let finalX = Math.min(cursorX, window.innerWidth - menuWidth - 10);
            let finalY;

            if (spaceBelow >= menuHeight || spaceBelow > spaceAbove) {
                // Show below cursor
                finalY = cursorY + lineHeight + 5;
            } else {
                // Show above cursor
                finalY = cursorY - menuHeight - 5;
            }

            // Ensure menu stays within viewport
            finalY = Math.max(10, Math.min(finalY, window.innerHeight - menuHeight - 10));
            finalX = Math.max(10, finalX);

            this.commandPosition = {
                x: finalX,
                y: finalY
            };

            this.showCommands = true;
            this.selectedCommand = 0;
        },

        hideCommandMenu() {
            this.showCommands = false;
        },

        insertCommand(textarea) {
            const command = this.commands[this.selectedCommand];
            const cursorPos = textarea.selectionStart;
            const textBefore = textarea.value.substring(0, cursorPos);
            const textAfter = textarea.value.substring(cursorPos);

            textarea.value = textBefore + command.text + textAfter;
            textarea.dispatchEvent(new Event('input'));

            const newPos = cursorPos + command.text.length;
            textarea.setSelectionRange(newPos, newPos);

            this.hideCommandMenu();
        },

        selectCommand(index, textarea) {
            this.selectedCommand = index;
            this.insertCommand(textarea);
        },

        // Handle text selection for formatting toolbar
        handleSelection(event) {
            const textarea = event.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;

            if (start !== end) {
                // Text is selected
                this.selectedText = textarea.value.substring(start, end);
                this.selectionStart = start;
                this.selectionEnd = end;
                this.showFormattingToolbar(textarea);
            } else {
                // No text selected
                this.hideFormattingToolbar();
            }
        },

        showFormattingToolbar(textarea) {
            const rect = textarea.getBoundingClientRect();
            const start = this.selectionStart;
            const textBeforeSelection = textarea.value.substring(0, start);
            const lines = textBeforeSelection.split('\n');
            const currentLine = lines.length - 1;
            const currentColumn = lines[lines.length - 1].length;

            const style = window.getComputedStyle(textarea);
            const lineHeight = parseInt(style.lineHeight) || 24;
            const fontSize = parseInt(style.fontSize) || 16;
            const paddingTop = parseInt(style.paddingTop) || 0;
            const paddingLeft = parseInt(style.paddingLeft) || 0;
            const charWidth = fontSize * 0.6;

            const selectionX = rect.left + paddingLeft + (currentColumn * charWidth);
            const selectionY = rect.top + paddingTop + (currentLine * lineHeight);

            // Position toolbar above selection
            this.toolbarPosition = {
                x: Math.max(10, Math.min(selectionX, window.innerWidth - 300)),
                y: Math.max(10, selectionY - 50)
            };

            this.showFormatToolbar = true;
        },

        hideFormattingToolbar() {
            this.showFormatToolbar = false;
        },

        // Formatting functions
        formatText(type, textarea) {
            const start = this.selectionStart;
            const end = this.selectionEnd;
            const selectedText = this.selectedText;
            const textBefore = textarea.value.substring(0, start);
            const textAfter = textarea.value.substring(end);

            let formattedText = '';
            let newCursorPos = end;

            switch (type) {
                case 'bold':
                    formattedText = `**${selectedText}**`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'italic':
                    formattedText = `*${selectedText}*`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'highlight':
                    formattedText = `==${selectedText}==`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'code':
                    formattedText = `\`${selectedText}\``;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'h1':
                    formattedText = `# ${selectedText}`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'h2':
                    formattedText = `## ${selectedText}`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'h3':
                    formattedText = `### ${selectedText}`;
                    newCursorPos = start + formattedText.length;
                    break;
                case 'h4':
                    formattedText = `#### ${selectedText}`;
                    newCursorPos = start + formattedText.length;
                    break;
                default:
                    formattedText = selectedText;
            }

            // Update textarea content
            textarea.value = textBefore + formattedText + textAfter;
            textarea.dispatchEvent(new Event('input'));

            // Set cursor position and hide toolbar
            textarea.setSelectionRange(newCursorPos, newCursorPos);
            this.hideFormattingToolbar();
            textarea.focus();
        }
    }
}