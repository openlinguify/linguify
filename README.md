<p align="center">
  <a href="https://www.openlinguify.com" target="_blank">
    <img src="backend/static/images/Linguify (2).png" alt="OpenLinguify" width="200" />
  </a>
</p>

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI/CD Pipeline](https://github.com/openlinguify/linguify/actions/workflows/ci-cd-pipeline.yml/badge.svg)](https://github.com/openlinguify/linguify/actions/workflows/ci-cd-pipeline.yml)
[![Languages: 4](https://img.shields.io/badge/Interface_Languages-4-green.svg)](https://github.com/openlinguify/linguify)
[![Translation Help Wanted](https://img.shields.io/badge/Translations-European_Languages_Priority-blue.svg)](https://github.com/openlinguify/linguify#-help-us-translate-openlinguify)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/openlinguify/linguify/blob/main/CONTRIBUTING.md)
[![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-orange.svg)](https://github.com/openlinguify/linguify/discussions)

## Vision

OpenLinguify is an open-source educational apps platform designed to break down language barriers and connect cultures through innovative technology. We're on a mission to make language acquisition accessible, engaging, and effective for learners at all levels.

**Currently supporting English, Spanish, Dutch, and French** — with your help, we can expand to even more languages!

## ✨ Why Contribute to OpenLinguify?

By joining our community of contributors, you'll:

- **Make a global impact** on language education accessibility
- **Solve interesting challenges** at the intersection of linguistics and technology
- **Build your portfolio** with meaningful open-source contributions
- **Connect with experts** across development, education, and language fields
- **Learn cutting-edge technologies** while creating something that matters

Whether you're a developer, linguist, teacher, designer, or language enthusiast — your skills can help revolutionize how people learn languages!

## 🚀 Core Features

OpenLinguify offers a comprehensive educational experience:

- **Interactive Learning Paths** – Carefully designed progression through our four core languages
- **Smart Vocabulary Builder** – Context-based word acquisition with native-speaker audio
- **Adaptive Grammar System** – Exercises that adjust to your learning pace
- **AI Conversation Practice** – Practice your language skills with AI-powered conversation partners
- **Spaced Repetition Flashcards** – Science-backed memory optimization techniques
- **Personal Language Notebook** – Capture and organize your own learning materials
- **Progress Dashboard** – Data-driven insights to track your language journey
- **Gamification Elements** – Stay motivated with achievements and streaks
- **GDPR Compliance** – Full account management with 30-day grace period for deletion

## 🛠️ Technology Stack

Our modern tech stack offers plenty of opportunities to enhance your skills:

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Django, Python, RESTful APIs
- **Database**: PostgreSQL
- **Templates**: Django Templates with i18n support
- **Styling**: CSS3 with CSS Custom Properties, Responsive Design
- **Authentication**: Django Auth, JWT with GDPR-compliant account management
- **UI/UX**: Modern CSS animations, accessibility-focused components
- **DevOps**: GitHub Actions, Docker
- **Testing**: Pytest, Django TestCase

## 🔥 How You Can Contribute

We welcome contributions of all types and sizes! Here's how to get started:

### Prerequisites

- **Python 3.8+**: [install guide](https://www.python.org/downloads/)
- **Poetry**: [install guide](https://python-poetry.org/docs/)
- **PostgreSQL**: [install guide](https://www.postgresql.org/download/)
- **Docker** (optional): [install guide](https://docs.docker.com/get-docker/)

### Code Contributions

1. **Set up your environment**:
   ```bash
   git clone https://github.com/openlinguify/linguify.git
   cd linguify
   
   # Backend setup
   cd backend
   poetry install
   poetry run python manage.py migrate
   poetry run python manage.py collectstatic
   poetry run python manage.py runserver
   
   # Portal setup (in a separate terminal)
   cd portal
   poetry install
   poetry run python manage.py migrate
   poetry run python manage.py runserver 8001
   ```

2. **Find your first issue**:
   - Check our [Good First Issues](https://github.com/openlinguify/linguify/labels/good%20first%20issue)
   - Browse [Help Wanted](https://github.com/openlinguify/linguify/labels/help%20wanted) for more challenges
   - See the [Project Board](https://github.com/openlinguify/linguify/projects) for current priorities

3. **Follow our development flow**:
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/amazing-feature`)
   - Make your changes with clear, descriptive commits
   - Push to your branch (`git push origin feature/amazing-feature`)
   - Open a Pull Request with detailed description

### Non-Code Contributions (Equally Valuable!)

- **Language Expertise**: Help improve content quality, translations, or language learning methodologies
- **Design**: Create UI components, illustrations, or improve user experience
- **Documentation**: Enhance guides, API docs, or learning resources
- **Testing**: Try features and report bugs or usability issues
- **Community Support**: Answer questions in discussions or help other contributors

### 🌍 Help Us Translate OpenLinguify

We're actively seeking people to make OpenLinguify accessible to learners worldwide! 

**Currently supported languages:**
- 🇬🇧 **English** (Complete)
- 🇫🇷 **French** (Complete) 
- 🇪🇸 **Spanish** (Complete)
- 🇳🇱 **Dutch** (Complete)

**Priority: European Languages First**
- 🇩🇪 **German** - *Help us get started!*
- 🇮🇹 **Italian** - *Translators needed*
- 🇵🇹 **Portuguese** - *Community requested*
- 🇵🇱 **Polish** - *Growing user base*
- 🇸🇪 **Swedish** - *Nordic expansion*
- 🇳🇴 **Norwegian** - *High interest*
- 🇩🇰 **Danish** - *Nordic completion*
- 🇫🇮 **Finnish** - *Nordic completion*
- 🇬🇷 **Greek** - *Educational heritage*
- 🇨🇿 **Czech** - *Central Europe focus*
- 🇭🇺 **Hungarian** - *Unique language family*
- 🇷🇴 **Romanian** - *Growing demand*
- 🇧🇬 **Bulgarian** - *Balkan expansion*
- 🇭🇷 **Croatian** - *Community request*
- 🇸🇰 **Slovak** - *Central Europe*
- 🇸🇮 **Slovenian** - *Complete Balkans*
- 🇪🇪 **Estonian** - *Baltic states*
- 🇱🇻 **Latvian** - *Baltic completion*
- 🇱🇹 **Lithuanian** - *Baltic completion*

**How to contribute translations:**

📖 **[Read our complete Translation Guide](docs/translations/translation-guide.md)** for detailed instructions!

**Quick start:**
1. **Check existing translations**: Browse i18n files in each app (e.g., `backend/apps/course/i18n/`)
2. **Choose your approach**: 
   - 🖥️ **Poedit** (beginner-friendly GUI)
   - ✏️ **Text editor** (for experienced translators)
   - 🛠️ **Django commands** (for developers)
3. **Follow the structure**: Each app has its own `i18n/` folder with `.po` files
4. **Test locally**: Compile with `msgfmt` and test in your browser
5. **Submit**: Create a Pull Request with your translated `.po` and `.mo` files

💡 **First time?** Start with the **course** app - it contains the core learning interface!

**Translation guidelines:**
- Maintain consistent tone (friendly, educational, encouraging)
- Adapt cultural references appropriately
- Keep technical terms consistent
- Test UI layouts with longer text lengths
- Consider right-to-left languages layout needs

**Need help?** Join our [Discord #translations channel](https://discord.gg/openlinguify) or open a [GitHub Discussion](https://github.com/openlinguify/linguify/discussions) tagged with "translations".

## 🌱 Perfect for First-Time Contributors

New to open source? OpenLinguify is an ideal project to start your journey:

- **Beginner-friendly issues** – Specially tagged for newcomers
- **Supportive community** – Friendly feedback on your contributions

## 🗺️ Roadmap & Opportunities

Help us tackle these exciting challenges:

- **European Languages Priority** – Adding interface support for all major European languages (German, Italian, Portuguese, Polish, Nordic languages, etc.)
- **Content Localization** – Adapting learning materials for different cultures and regions  
- **Language Learning Features** – Adding support for more languages beyond our current four
- **Personalized Learning** – Building AI-driven learning recommendations
- **Mobile Experience** – Develop a mobile app part
- **Educator Tools** – Developing features for classroom use cases for the education ecosystem
- **RTL Language Support** – Adding proper support for right-to-left languages like Arabic

Check our complete [project roadmap](https://github.com/openlinguify/linguify/wiki/Roadmap) for more details.

## 📚 Resources

- [Contribution Guide](https://github.com/openlinguify/linguify/blob/main/CONTRIBUTING.md)
- [Translation Guide](docs/translations/translation-guide.md) - *Complete step-by-step translation tutorial*
- [Code of Conduct](https://github.com/openlinguify/linguify/blob/main/CODE_OF_CONDUCT.md)
- [Development Documentation](https://github.com/openlinguify/linguify/wiki/Development-Guide)
- [API References](https://github.com/openlinguify/linguify/wiki/API-Docs)
- [i18n Files](https://github.com/openlinguify/linguify/tree/main/backend/locale) - *Current translations*

## 🌟 Join Our Community

- **Discord**: [Join our server](https://discord.gg/openlinguify) for real-time discussions
- **Discussions**: Participate in [GitHub Discussions](https://github.com/openlinguify/linguify/discussions)
- **Twitter**: Follow us [@OpenLinguify](https://twitter.com/openlinguify) for updates
- **Website**: Visit [OpenLinguify.com](https://www.openlinguify.com) for more information

## 📄 License

OpenLinguify is open source software licensed under the [GNU General Public License v3.0](LICENSE).

## 📣 Contact

Questions about contributing? Email us at dev@openlinguify.com or reach out on Discord.

---

**Your contributions can help millions learn new languages!** We can't wait to see what you build with us.
