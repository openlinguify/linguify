/** @odoo-module **/

import { Component } from "@odoo/owl";

export class Navbar extends Component {
    static template = "language_learning.Navbar";
    static props = {
        selectedLanguage: String,
        selectedLanguageName: String,
        userStreak: Number,
        onLanguageChange: { type: Function, optional: true }
    };

    onLanguageSelect(languageCode) {
        if (this.props.onLanguageChange) {
            this.props.onLanguageChange(languageCode);
        }
    }

    get languageFlag() {
        const flagMap = {
            'EN': '🇬🇧',
            'FR': '🇫🇷',
            'ES': '🇪🇸',
            'DE': '🇩🇪',
            'IT': '🇮🇹'
        };
        return flagMap[this.props.selectedLanguage] || '🌍';
    }
}