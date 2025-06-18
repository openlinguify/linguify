// Helper functions for TheoryContent admin form
window.addEventListener('load', function() {
    // Enhanced templates with proper translations
    const templates = {
        dates: {
            en: {
                content: "Days of the week, months, and date formats",
                explanation: "In English, dates use ordinal numbers for days (1st, 2nd, 3rd). Months start with capital letters. There are two main formats: American (MM/DD/YYYY) and British (DD/MM/YYYY).",
                formula: "American: Month Day, Year | British: Day Month Year",
                example: "American: January 15, 2024 | British: 15 January 2024",
                exception: "The first day is '1st', second is '2nd', third is '3rd', all others end in 'th'"
            },
            fr: {
                content: "Les jours de la semaine, les mois et les formats de dates",
                explanation: "En français, les dates utilisent les nombres cardinaux sauf pour le premier jour. Les mois s'écrivent en minuscule. Le format standard est : le jour mois année.",
                formula: "le + jour + mois + année",
                example: "le 15 janvier 2024",
                exception: "Premier jour du mois : 'le premier janvier' ou 'le 1er janvier'"
            },
            es: {
                content: "Los días de la semana, los meses y los formatos de fecha",
                explanation: "En español, las fechas usan números cardinales excepto el primero. Los meses se escriben en minúscula. El formato es: día de mes de año.",
                formula: "día + de + mes + de + año",
                example: "15 de enero de 2024",
                exception: "Primer día: 'primero de enero' o 'uno de enero'"
            },
            nl: {
                content: "Dagen van de week, maanden en datumformaten",
                explanation: "In het Nederlands gebruiken datums gewone getallen. Maanden beginnen met kleine letter. Het formaat is: dag maand jaar.",
                formula: "dag + maand + jaar",
                example: "15 januari 2024",
                exception: "Numeriek formaat: DD-MM-JJJJ (15-01-2024)"
            }
        },
        plurals: {
            en: {
                content: "Forming plural nouns in English",
                explanation: "In English, most plurals are formed by adding -s or -es to the end of a noun. This is one of the most fundamental grammar rules.",
                formula: "Singular + -s/-es = Plural",
                example: "cat → cats, box → boxes, city → cities",
                exception: "Irregular plurals: man → men, child → children, mouse → mice"
            },
            fr: {
                content: "Formation des noms au pluriel en français",
                explanation: "En français, la plupart des pluriels se forment en ajoutant -s à la fin du nom. C'est l'une des règles grammaticales fondamentales.",
                formula: "Singulier + -s = Pluriel",
                example: "chat → chats, livre → livres, ville → villes",
                exception: "Pluriels irréguliers: cheval → chevaux, œil → yeux, ciel → cieux"
            },
            es: {
                content: "Formación del plural de los sustantivos en español",
                explanation: "En español, la mayoría de los plurales se forman añadiendo -s o -es al final del sustantivo según su terminación.",
                formula: "Singular + -s/-es = Plural",
                example: "gato → gatos, caja → cajas, ciudad → ciudades",
                exception: "Plurales irregulares: crisis → crisis, análisis → análisis"
            },
            nl: {
                content: "Meervoudsvorming van zelfstandige naamwoorden in het Nederlands",
                explanation: "In het Nederlands worden meervouden meestal gevormd door -en of -s toe te voegen aan het einde van een zelfstandig naamwoord.",
                formula: "Enkelvoud + -en/-s = Meervoud",
                example: "kat → katten, boek → boeken, huis → huizen",
                exception: "Onregelmatige meervouden: kind → kinderen, stad → steden"
            }
        }
    };
    
    // Create template UI in the first fieldset
    const contentLessonField = document.querySelector('#id_content_lesson');
    if (contentLessonField) {
        const fieldset = contentLessonField.closest('fieldset');
        
        // Add template selector
        const templateDiv = document.createElement('div');
        templateDiv.style.marginTop = '15px';
        templateDiv.style.padding = '10px';
        templateDiv.style.backgroundColor = '#f5f5f5';
        templateDiv.style.borderRadius = '4px';
        templateDiv.innerHTML = `
            <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Quick Fill Templates</h3>
            <label for="template-selector">Select a template:</label>
            <select id="template-selector" style="margin: 0 10px;">
                <option value="">-- Choose a template --</option>
                <option value="dates">Dates and Times</option>
                <option value="plurals">Plural Forms</option>
            </select>
            <button type="button" id="apply-template">Apply Template</button>
        `;
        
        fieldset.appendChild(templateDiv);
    }
    
    // Auto-fill template selection
    const templateSelector = document.getElementById('template-selector');
    const applyTemplateBtn = document.getElementById('apply-template');
    
    if (applyTemplateBtn && templateSelector) {
        applyTemplateBtn.addEventListener('click', function() {
            const template = templates[templateSelector.value];
            if (template) {
                // Fill all language fields
                const languages = ['en', 'fr', 'es', 'nl'];
                languages.forEach(lang => {
                    if (template[lang]) {
                        const contentField = document.querySelector(`#id_content_${lang}`);
                        const explanationField = document.querySelector(`#id_explication_${lang}`);
                        const formulaField = document.querySelector(`#id_formula_${lang}`);
                        const exampleField = document.querySelector(`#id_example_${lang}`);
                        const exceptionField = document.querySelector(`#id_exception_${lang}`);
                        
                        if (contentField && template[lang].content) contentField.value = template[lang].content;
                        if (explanationField && template[lang].explanation) explanationField.value = template[lang].explanation;
                        if (formulaField && template[lang].formula) formulaField.value = template[lang].formula;
                        if (exampleField && template[lang].example) exampleField.value = template[lang].example;
                        if (exceptionField && template[lang].exception) exceptionField.value = template[lang].exception;
                    }
                });
                
                // Show success message
                const successMsg = document.createElement('div');
                successMsg.style.cssText = 'background-color: #4CAF50; color: white; padding: 10px; border-radius: 4px; margin: 10px 0;';
                successMsg.textContent = 'Template applied successfully!';
                applyTemplateBtn.parentNode.appendChild(successMsg);
                setTimeout(() => successMsg.remove(), 3000);
            }
        });
    }
    
    // Add helpful message for content_lesson field
    const contentLessonSelect = document.querySelector('#id_content_lesson');
    if (contentLessonSelect) {
        const helpDiv = document.createElement('div');
        helpDiv.className = 'help';
        helpDiv.style.cssText = 'background-color: #e3f2fd; padding: 10px; border-radius: 4px; margin-top: 5px; color: #0d47a1;';
        helpDiv.innerHTML = '⚠️ <strong>Important:</strong> Only ContentLessons without existing TheoryContent are shown. If you can\'t find the lesson you want, it may already have theory content.';
        contentLessonSelect.parentNode.appendChild(helpDiv);
        
        // Check if no options are available
        if (contentLessonSelect.options.length <= 1) {  // Only the empty option
            const warningDiv = document.createElement('div');
            warningDiv.style.cssText = 'background-color: #ffebee; color: #c62828; padding: 10px; border-radius: 4px; margin-top: 10px;';
            warningDiv.innerHTML = '⚠️ <strong>Warning:</strong> No ContentLessons without TheoryContent are available. You may need to create a new ContentLesson first.';
            contentLessonSelect.parentNode.appendChild(warningDiv);
        }
    }
    
    // Fix JSON field initialization
    const jsonFormatCheckbox = document.querySelector('#id_using_json_format');
    const jsonContentField = document.querySelector('#id_language_specific_content');
    
    if (jsonFormatCheckbox && jsonContentField) {
        // Function to initialize JSON content
        function initializeJSONContent() {
            if (jsonFormatCheckbox.checked) {
                const currentValue = jsonContentField.value.trim();
                if (!currentValue || currentValue === 'null' || currentValue === '{}') {
                    // Set default JSON structure
                    const defaultContent = {
                        "en": {"content": "", "explanation": ""},
                        "fr": {"content": "", "explanation": ""},
                        "es": {"content": "", "explanation": ""},
                        "nl": {"content": "", "explanation": ""}
                    };
                    jsonContentField.value = JSON.stringify(defaultContent, null, 2);
                    
                    // Trigger any JSON validation/formatting
                    if (window.JSONEditor && jsonContentField.JSONEditor) {
                        jsonContentField.JSONEditor.setValue(defaultContent);
                    }
                }
            }
        }
        
        // Initialize on page load
        initializeJSONContent();
        
        // Initialize when checkbox is toggled
        jsonFormatCheckbox.addEventListener('change', initializeJSONContent);
    }
    
    // Add minimum content requirements info
    const changeForm = document.querySelector('#theorycontent_form');
    if (changeForm && !document.querySelector('.minimum-requirements')) {
        const requirementsDiv = document.createElement('div');
        requirementsDiv.className = 'minimum-requirements';
        requirementsDiv.style.cssText = 'background-color: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 4px; border: 1px solid #ffc107;';
        requirementsDiv.innerHTML = `
            <h3 style="margin: 0 0 10px 0; color: #856404;">Minimum Content Requirements</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Content fields:</strong> Must contain at least 3-5 words describing the topic</li>
                <li><strong>Explanation fields:</strong> Must contain at least 10-15 words explaining the concept</li>
                <li><strong>Formula/Example/Exception:</strong> Optional but recommended when applicable</li>
            </ul>
            <p style="margin: 10px 0 0 0; color: #856404;"><strong>Note:</strong> Single letters or minimal content like "f" will be rejected.</p>
        `;
        
        const firstFieldset = changeForm.querySelector('fieldset');
        if (firstFieldset) {
            firstFieldset.parentNode.insertBefore(requirementsDiv, firstFieldset.nextSibling);
        }
    }
});