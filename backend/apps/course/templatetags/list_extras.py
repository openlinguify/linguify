from django import template

register = template.Library()

@register.filter
def get_item(list_obj, index):
    """Permet d'accéder à un élément d'une liste par son indice."""
    try:
        # Convertir index en entier si c'est une chaîne de caractères
        if isinstance(index, str):
            index = int(index)
        
        # Vérifier si l'index est valide
        if 0 <= index < len(list_obj):
            return list_obj[index]
        return None
    except (IndexError, ValueError, TypeError):
        return None