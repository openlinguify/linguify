# -*- coding: utf-8 -*-
"""
XML Template Parser for Notebook App
Permet de lire et utiliser les templates XML définis dans templates.xml
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
import os


class XMLTemplateParser:
    """Parser pour les templates XML de type Odoo/Linguify"""

    def __init__(self, xml_file_path: str = None):
        if xml_file_path is None:
            # Dossier par défaut contenant tous les fichiers XML
            self.xml_dir = os.path.join(
                settings.BASE_DIR,
                'apps', 'notebook', 'templates'
            )
        else:
            if os.path.isdir(xml_file_path):
                self.xml_dir = xml_file_path
            else:
                self.xml_dir = os.path.dirname(xml_file_path)

        self.views = {}
        self.actions = {}
        self.menus = {}
        self._parse_all_xml_files()

    def _parse_all_xml_files(self) -> None:
        """Parse tous les fichiers XML du dossier"""
        xml_files = []

        # Chercher tous les fichiers XML
        for root, dirs, files in os.walk(self.xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))

        # Parser chaque fichier XML
        for xml_file in xml_files:
            self._parse_single_xml_file(xml_file)

        print(f"✅ Parsed {len(xml_files)} XML files: {len(self.views)} views, {len(self.actions)} actions, {len(self.menus)} menus")

    def _parse_single_xml_file(self, xml_file_path: str) -> None:
        """Parse un seul fichier XML"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Parser les vues (support pour ir.ui.view et linguify.ui.view)
            for record in root.findall('.//record[@model="ir.ui.view"]') + root.findall('.//record[@model="linguify.ui.view"]'):
                view_id = record.get('id')
                view_data = {'source_file': os.path.basename(xml_file_path)}

                for field in record.findall('field'):
                    field_name = field.get('name')
                    field_value = field.text or ''

                    # Traitement spécial pour le champ arch qui contient du XML
                    if field_name == 'arch':
                        field_type = field.get('type', 'string')
                        if field_type == 'xml':
                            # Parser le contenu XML interne
                            arch_content = self._parse_arch_content(field)
                            view_data[field_name] = arch_content
                        else:
                            view_data[field_name] = field_value
                    else:
                        view_data[field_name] = field_value

                self.views[view_id] = view_data

            # Parser les actions
            for record in root.findall('.//record[@model="ir.actions.act_window"]'):
                action_id = record.get('id')
                action_data = {'source_file': os.path.basename(xml_file_path)}

                for field in record.findall('field'):
                    field_name = field.get('name')
                    field_value = field.text or ''
                    action_data[field_name] = field_value

                self.actions[action_id] = action_data

            # Parser les menus
            for menuitem in root.findall('.//menuitem'):
                menu_id = menuitem.get('id')
                menu_data = {
                    'source_file': os.path.basename(xml_file_path),
                    'name': menuitem.get('name'),
                    'parent': menuitem.get('parent'),
                    'action': menuitem.get('action'),
                    'sequence': menuitem.get('sequence', '10'),
                }
                self.menus[menu_id] = menu_data

        except ET.ParseError as e:
            print(f"Erreur lors du parsing XML {xml_file_path}: {e}")
        except FileNotFoundError:
            print(f"Fichier XML non trouvé : {xml_file_path}")

    def _parse_arch_content(self, arch_field) -> Dict[str, Any]:
        """Parse le contenu du champ arch qui contient la structure de la vue"""
        arch_data = {
            'type': None,
            'fields': [],
            'structure': {},
            'raw_xml': ''
        }

        # Récupérer le premier élément enfant (form, tree, div, etc.)
        for child in arch_field:
            if child.tag in ['form', 'tree', 'search', 'kanban']:
                arch_data['type'] = child.tag
                arch_data['structure'] = self._parse_view_element(child)
                break
            elif child.tag in ['div', 'section', 'html']:
                # Pour les éléments HTML personnalisés (comme pour la sidebar)
                arch_data['type'] = child.tag
                arch_data['structure'] = self._parse_view_element(child)
                # Conserver le XML brut pour les éléments HTML
                arch_data['raw_xml'] = ET.tostring(child, encoding='unicode', method='xml')
                break

        return arch_data

    def _parse_view_element(self, element) -> Dict[str, Any]:
        """Parse récursivement un élément de vue XML"""
        result = {
            'tag': element.tag,
            'attributes': element.attrib.copy(),
            'children': [],
            'fields': []
        }

        # Parser les éléments enfants
        for child in element:
            if child.tag == 'field':
                # Traitement spécial pour les champs
                field_info = {
                    'name': child.get('name'),
                    'attributes': child.attrib.copy()
                }
                result['fields'].append(field_info)
            else:
                # Traitement récursif pour les autres éléments
                result['children'].append(self._parse_view_element(child))

        return result

    def get_view(self, view_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une vue par son ID"""
        return self.views.get(view_id)

    def get_all_views(self) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les vues parsées"""
        return self.views

    def get_all_actions(self) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les actions parsées"""
        return self.actions

    def get_all_menus(self) -> Dict[str, Dict[str, Any]]:
        """Récupère tous les menus parsés"""
        return self.menus

    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une action par son ID"""
        return self.actions.get(action_id)

    def get_menu(self, menu_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un menu par son ID"""
        return self.menus.get(menu_id)

    def get_views_by_model(self, model_name: str) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les vues pour un modèle donné"""
        model_views = {}
        for view_id, view_data in self.views.items():
            if view_data.get('model') == model_name:
                model_views[view_id] = view_data
        return model_views

    def get_views_by_type(self, view_type: str) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les vues d'un type donné (form, tree, kanban, etc.)"""
        type_views = {}
        for view_id, view_data in self.views.items():
            if view_data.get('arch', {}).get('type') == view_type:
                type_views[view_id] = view_data
        return type_views

    def get_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques sur les éléments parsés"""
        view_types = {}
        source_files = set()

        for view_data in self.views.values():
            view_type = view_data.get('arch', {}).get('type', 'unknown')
            view_types[view_type] = view_types.get(view_type, 0) + 1
            source_files.add(view_data.get('source_file', 'unknown'))

        return {
            'total_views': len(self.views),
            'total_actions': len(self.actions),
            'total_menus': len(self.menus),
            'view_types': view_types,
            'source_files': list(source_files),
            'files_count': len(source_files)
        }

    def generate_django_form_fields(self, view_id: str) -> List[str]:
        """Génère une liste des champs Django à partir d'une vue XML"""
        view = self.get_view(view_id)
        if not view or 'arch' not in view:
            return []

        fields = []
        arch = view['arch']

        if 'structure' in arch:
            fields = self._extract_fields_from_structure(arch['structure'])

        return fields

    def _extract_fields_from_structure(self, structure: Dict[str, Any]) -> List[str]:
        """Extrait récursivement les noms de champs d'une structure de vue"""
        fields = []

        # Ajouter les champs directs
        for field in structure.get('fields', []):
            fields.append(field['name'])

        # Parcourir récursivement les éléments enfants
        for child in structure.get('children', []):
            fields.extend(self._extract_fields_from_structure(child))

        return fields

    def render_as_html_form(self, view_id: str, instance_data: Dict = None) -> str:
        """Convertit une vue XML en formulaire HTML Django"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        if 'arch' not in view or view['arch'].get('type') != 'form':
            return f"<p>Vue '{view_id}' n'est pas un formulaire</p>"

        fields = self.generate_django_form_fields(view_id)
        form_title = view.get('name', 'Formulaire')

        # Générer le HTML du formulaire
        html = f"<form class='xml-generated-form'>\n"
        html += f"<h3>{form_title}</h3>\n"

        for field_name in fields:
            field_value = instance_data.get(field_name, '') if instance_data else ''
            html += f"""
            <div class="form-group">
                <label for="{field_name}">{field_name.replace('_', ' ').title()}:</label>
                <input type="text" id="{field_name}" name="{field_name}" value="{field_value}" class="form-control">
            </div>
            """

        html += "</form>"
        return html

    def render_as_table(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML tree en tableau HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        if 'arch' not in view or view['arch'].get('type') != 'tree':
            return f"<p>Vue '{view_id}' n'est pas une vue liste</p>"

        fields = self.generate_django_form_fields(view_id)

        # Générer le HTML du tableau
        html = "<table class='xml-generated-table table table-striped'>\n"
        html += "<thead><tr>\n"

        for field_name in fields:
            html += f"<th>{field_name.replace('_', ' ').title()}</th>\n"

        html += "</tr></thead>\n<tbody>\n"

        if data_list:
            for item in data_list:
                html += "<tr>\n"
                for field_name in fields:
                    value = item.get(field_name, '-')
                    html += f"<td>{value}</td>\n"
                html += "</tr>\n"
        else:
            html += "<tr><td colspan='{}'>Aucune donnée disponible</td></tr>\n".format(len(fields))

        html += "</tbody></table>"
        return html

    def render_as_kanban(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML kanban en cartes HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        if 'arch' not in view or view['arch'].get('type') != 'kanban':
            return f"<p>Vue '{view_id}' n'est pas une vue kanban</p>"

        fields = self.generate_django_form_fields(view_id)

        # Générer le HTML des cartes kanban
        html = "<div class='xml-generated-kanban'>\n"
        html += "<h3>Vue Kanban</h3>\n"

        if data_list:
            html += "<div class='kanban-board'>\n"
            for item in data_list:
                html += "<div class='kanban-card'>\n"

                # Titre principal
                title = item.get('title', item.get('name', 'Sans titre'))
                html += f"<div class='kanban-card-title'>{title}</div>\n"

                # Autres champs
                html += "<div class='kanban-card-content'>\n"
                for field_name in fields[:4]:  # Limiter à 4 champs pour la lisibilité
                    if field_name not in ['title', 'name']:
                        value = item.get(field_name, '-')
                        html += f"<div class='kanban-field'><strong>{field_name.replace('_', ' ').title()}:</strong> {value}</div>\n"
                html += "</div>\n"

                html += "</div>\n"  # Fermer kanban-card
            html += "</div>\n"  # Fermer kanban-board
        else:
            html += "<div class='kanban-empty'>Aucune donnée disponible</div>\n"

        html += "</div>"
        return html

    def render_as_search(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML search en interface de recherche HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        if 'arch' not in view or view['arch'].get('type') != 'search':
            return f"<p>Vue '{view_id}' n'est pas une vue de recherche</p>"

        fields = self.generate_django_form_fields(view_id)

        # Générer le HTML de l'interface de recherche
        html = "<div class='xml-generated-search'>\n"
        html += "<h3>Interface de Recherche</h3>\n"

        html += "<form class='search-form'>\n"
        html += "<div class='search-fields'>\n"

        for field_name in fields[:6]:  # Limiter le nombre de champs
            html += f"""
            <div class="search-field">
                <label for="search_{field_name}">{field_name.replace('_', ' ').title()}:</label>
                <input type="text" id="search_{field_name}" name="{field_name}" class="form-control" placeholder="Rechercher par {field_name}...">
            </div>
            """

        html += "</div>\n"
        html += "<div class='search-actions'>\n"
        html += "<button type='submit' class='btn btn-primary'>🔍 Rechercher</button>\n"
        html += "<button type='reset' class='btn btn-secondary'>🔄 Réinitialiser</button>\n"
        html += "</div>\n"
        html += "</form>\n"

        # Ajouter des filtres prédéfinis si disponibles
        html += "<div class='search-filters'>\n"
        html += "<h4>Filtres rapides:</h4>\n"
        html += "<div class='filter-buttons'>\n"
        html += "<button class='btn btn-outline-primary btn-sm'>📌 Épinglés</button>\n"
        html += "<button class='btn btn-outline-primary btn-sm'>🗄️ Archivés</button>\n"
        html += "<button class='btn btn-outline-primary btn-sm'>⭐ Priorité haute</button>\n"
        html += "<button class='btn btn-outline-primary btn-sm'>📚 Vocabulaire</button>\n"
        html += "</div>\n"
        html += "</div>\n"

        html += "</div>"
        return html

    def render_as_calendar(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML calendar en calendrier HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        # Générer un calendrier simple
        html = "<div class='xml-generated-calendar'>\n"
        html += "<h3>Vue Calendrier</h3>\n"
        html += "<div class='calendar-container'>\n"

        if data_list:
            html += "<div class='calendar-events'>\n"
            for item in data_list:
                title = item.get('title', item.get('name', 'Événement'))
                date = item.get('created_at', item.get('date', 'Date inconnue'))
                priority = item.get('priority', 'MEDIUM')

                priority_class = {
                    'HIGH': 'event-high',
                    'MEDIUM': 'event-medium',
                    'LOW': 'event-low'
                }.get(priority, 'event-medium')

                html += f"""
                <div class="calendar-event {priority_class}">
                    <div class="event-title">{title}</div>
                    <div class="event-date">{date}</div>
                    <div class="event-priority">Priorité: {priority}</div>
                </div>
                """
            html += "</div>\n"
        else:
            html += "<div class='calendar-empty'>Aucun événement</div>\n"

        html += "</div>\n"
        html += "</div>"
        return html

    def render_as_graph(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML graph en graphique HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        # Générer un graphique simple avec Chart.js
        html = "<div class='xml-generated-graph'>\n"
        html += "<h3>Vue Graphique</h3>\n"
        html += "<canvas id='xmlChart' width='400' height='200'></canvas>\n"

        # Ajouter des données d'exemple
        html += """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        const ctx = document.getElementById('xmlChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Vocabulaire', 'Grammaire', 'Expression', 'Culture'],
                datasets: [{
                    label: 'Nombre de notes',
                    data: [12, 19, 8, 5],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 205, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        </script>
        """

        html += "</div>"
        return html

    def render_as_dashboard(self, view_id: str, data_list: List[Dict] = None) -> str:
        """Convertit une vue XML dashboard en tableau de bord HTML"""
        view = self.get_view(view_id)
        if not view:
            return f"<p>Vue '{view_id}' non trouvée</p>"

        # Générer un tableau de bord
        html = "<div class='xml-generated-dashboard'>\n"
        html += "<h3>Tableau de Bord</h3>\n"

        html += "<div class='dashboard-stats'>\n"
        html += """
        <div class="stat-card">
            <div class="stat-number">26</div>
            <div class="stat-label">Total Notes</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">8</div>
            <div class="stat-label">À réviser</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">4</div>
            <div class="stat-label">Langues</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">85%</div>
            <div class="stat-label">Progression</div>
        </div>
        """
        html += "</div>\n"

        html += "<div class='dashboard-charts'>\n"
        html += "<div class='chart-container'>\n"
        html += "<h4>Répartition par type</h4>\n"
        html += "<canvas id='typeChart' width='300' height='200'></canvas>\n"
        html += "</div>\n"
        html += "</div>\n"

        html += "</div>"
        return html


# Instance globale du parser
xml_parser = XMLTemplateParser()


def reload_xml_parser():
    """Recharge le parser XML global"""
    global xml_parser
    xml_parser = XMLTemplateParser()
    return xml_parser


def get_xml_view_data(view_id: str) -> Dict[str, Any]:
    """Helper function pour récupérer les données d'une vue XML"""
    return xml_parser.get_view(view_id)


def render_xml_view_as_html(view_id: str, data=None) -> str:
    """Helper function pour rendre une vue XML en HTML"""
    view = xml_parser.get_view(view_id)
    if not view:
        return f"<p>Vue '{view_id}' non trouvée</p>"

    view_type = view.get('arch', {}).get('type', 'unknown')

    # Mapping des types de vues vers leurs méthodes de rendu
    renderers = {
        'form': xml_parser.render_as_html_form,
        'tree': xml_parser.render_as_table,
        'kanban': xml_parser.render_as_kanban,
        'search': xml_parser.render_as_search,
        'calendar': xml_parser.render_as_calendar,
        'graph': xml_parser.render_as_graph,
        'dashboard': xml_parser.render_as_dashboard,
    }

    renderer = renderers.get(view_type)
    if renderer:
        return renderer(view_id, data)
    else:
        return f"<p>Type de vue '{view_type}' non supporté</p>"


def render_xml_sidebar(context_data: Dict[str, Any]) -> str:
    """Rendu de la sidebar à partir de la vue XML notebook_sidebar_view"""
    sidebar_view = xml_parser.get_view('notebook_sidebar_view')
    if not sidebar_view:
        print("❌ Vue 'notebook_sidebar_view' non trouvée")
        return render_fallback_sidebar(context_data)

    print(f"✅ Vue trouvée: {sidebar_view}")

    # Extraire l'architecture XML
    arch = sidebar_view.get('arch', {})
    print(f"🏗️ Architecture brute: {arch}")

    # Essayer différents formats de stockage de l'arch
    arch_string = ''
    if isinstance(arch, dict):
        # Essayer d'abord le XML brut
        arch_string = arch.get('raw_xml', '') or arch.get('content', '') or arch.get('data', '') or str(arch.get('xml', ''))
    elif isinstance(arch, str):
        arch_string = arch
    else:
        arch_string = str(arch)

    print(f"🏗️ Architecture string: {arch_string[:200]}...")

    if not arch_string or arch_string == '{}':
        print("❌ Architecture XML vide")
        return render_fallback_sidebar(context_data)

    # Parser le contenu XML pour générer le HTML
    try:
        # Parse l'architecture XML
        import xml.etree.ElementTree as ET

        # Si c'est du XML raw, le parser directement sans wrapper
        if arch_string.strip().startswith('<'):
            arch_root = ET.fromstring(arch_string)
        else:
            # Sinon, wrapper dans un élément root
            arch_root = ET.fromstring(f"<root>{arch_string}</root>")

        # Convertir le XML en HTML en substituant les variables
        html = _convert_xml_to_html(arch_root, context_data)
        print(f"✅ HTML généré: {len(html)} caractères")
        return html

    except Exception as e:
        print(f"❌ Erreur lors du parsing XML de la sidebar: {e}")
        import traceback
        traceback.print_exc()
        return render_fallback_sidebar(context_data)


def _convert_xml_to_html(element, context_data: Dict[str, Any]) -> str:
    """Convertit un élément XML en HTML en substituant les champs"""
    if element.tag == 'root':
        # Pour l'élément racine, traiter tous les enfants
        html = ""
        for child in element:
            html += _convert_xml_to_html(child, context_data)
        return html

    elif element.tag == 'field':
        # Remplacer les champs par les valeurs du contexte ou créer des inputs
        field_name = element.get('name', '')
        invisible = element.get('invisible') == '1'

        if field_name == 'view_id':
            return str(context_data.get('view_id', 'Unknown'))
        elif field_name == 'model_name':
            return str(context_data.get('model_name', ''))
        elif field_name == 'view_type':
            return str(context_data.get('view_type', ''))
        elif field_name == 'stats_total':
            return str(context_data.get('stats', {}).get('total', 0))
        elif field_name == 'stats_pinned':
            return str(context_data.get('stats', {}).get('pinned', 0))
        elif field_name == 'stats_archived':
            return str(context_data.get('stats', {}).get('archived', 0))
        elif field_name == 'id':
            if invisible:
                return '<input type="hidden" id="noteId" value="">'
            return '<input type="hidden" id="noteId" value="">'
        elif field_name == 'title':
            placeholder = element.get('placeholder', 'Titre de la note')
            class_attr = element.get('class', 'form-control form-control-sm')
            return f'<label for="noteTitle" class="form-label">Titre</label><input type="text" class="{class_attr}" id="noteTitle" placeholder="{placeholder}">'
        elif field_name == 'content':
            placeholder = element.get('placeholder', 'Contenu de la note')
            class_attr = element.get('class', 'form-control form-control-sm')
            rows = element.get('rows', '4')
            return f'<label for="noteContent" class="form-label">Contenu</label><textarea class="{class_attr}" id="noteContent" rows="{rows}" placeholder="{placeholder}"></textarea>'
        elif field_name == 'language':
            class_attr = element.get('class', 'form-select form-select-sm')
            # Traiter les options
            options_html = ""
            for child in element:
                if child.tag == 'option':
                    value = child.get('value', '')
                    text = child.text or ''
                    options_html += f'<option value="{value}">{text}</option>'
            return f'<label for="noteLanguage" class="form-label">Langue</label><select class="{class_attr}" id="noteLanguage">{options_html}</select>'
        elif field_name == 'priority':
            class_attr = element.get('class', 'form-select form-select-sm')
            # Traiter les options
            options_html = ""
            for child in element:
                if child.tag == 'option':
                    value = child.get('value', '')
                    text = child.text or ''
                    selected = ' selected' if child.get('selected') == '1' else ''
                    options_html += f'<option value="{value}"{selected}>{text}</option>'
            return f'<label for="notePriority" class="form-label">Priorité</label><select class="{class_attr}" id="notePriority">{options_html}</select>'
        else:
            return f"[{field_name}]"

    elif element.tag == 'group':
        # Convertir group en div avec classes Bootstrap
        col = element.get('col', '1')
        if col == '2':
            # Groupe avec 2 colonnes
            children_html = ""
            children = list(element)
            for i, child in enumerate(children):
                child_html = _convert_xml_to_html(child, context_data)
                col_class = 'col-6' if len(children) == 2 else 'col-12'
                children_html += f'<div class="{col_class}">{child_html}</div>'
            return f'<div class="row">{children_html}</div>'
        else:
            # Groupe simple
            children_html = ""
            for child in element:
                children_html += _convert_xml_to_html(child, context_data)
            return f'<div class="mb-3">{children_html}</div>'

    elif element.tag == 'footer':
        # Convertir footer en div avec boutons
        children_html = ""
        for child in element:
            children_html += _convert_xml_to_html(child, context_data)
        return f'<div class="mt-3 d-grid gap-2">{children_html}</div>'

    elif element.tag == 'button':
        # Traiter les boutons spéciaux
        special = element.get('special', '')
        btn_type = element.get('type', 'button')
        class_attr = element.get('class', 'btn btn-primary btn-sm')
        text = element.text or ''

        if special == 'save':
            return f'<button type="{btn_type}" class="{class_attr}" onclick="saveNote()">{text}</button>'
        elif special == 'cancel':
            return f'<button type="{btn_type}" class="{class_attr}" onclick="clearForm()">{text}</button>'
        else:
            # Bouton normal - copier tous les attributs
            attrs = []
            for key, value in element.attrib.items():
                if key != 'special':  # Exclure special
                    attrs.append(f'{key}="{value}"')
            attr_string = ' ' + ' '.join(attrs) if attrs else ''
            return f'<button{attr_string}>{text}</button>'

    else:
        # Pour les autres éléments, créer la balise HTML
        tag = element.tag
        attrs = []

        # Copier les attributs
        for key, value in element.attrib.items():
            attrs.append(f'{key}="{value}"')

        attr_string = ' ' + ' '.join(attrs) if attrs else ''

        # Contenu de l'élément
        text = element.text or ''

        # Traiter les enfants
        children_html = ""
        for child in element:
            children_html += _convert_xml_to_html(child, context_data)

        # Ajouter le texte après les enfants
        tail = element.tail or ''

        return f"<{tag}{attr_string}>{text}{children_html}</{tag}>{tail}"


def render_fallback_sidebar(context_data: Dict[str, Any]) -> str:
    """Fallback HTML sidebar si la vue XML n'est pas disponible"""
    stats = context_data.get('stats', {})
    return f"""
    <div class="sidebar-content">
        <div class="page-header-sidebar">
            <h5>🔍 Vue: {context_data.get('view_id', 'Unknown')}</h5>
            <small class="text-muted">{context_data.get('model_name', '')} | {context_data.get('view_type', '')}</small>
        </div>
        <div class="actions-bar">
            <h5>⚡ Actions</h5>
            <div class="stats-cards">
                <div class="stat-card">
                    <h6>Total</h6>
                    <h4>{stats.get('total', 0)}</h4>
                </div>
            </div>
        </div>
    </div>
    """