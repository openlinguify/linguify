from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary by key.
    Usage: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key, 0)

@register.filter
def level_color(level):
    """
    Return a CSS color class based on the level.
    Usage: {{ unit.level|level_color }}
    """
    color_map = {
        'A1': 'success',
        'A2': 'info', 
        'B1': 'warning',
        'B2': 'orange',
        'C1': 'danger',
        'C2': 'purple'
    }
    return color_map.get(level, 'secondary')

@register.filter
def content_type_icon(content_type):
    """
    Return a FontAwesome icon class based on content type.
    Usage: {{ content.content_type|content_type_icon }}
    """
    icon_map = {
        'Theory': 'fas fa-book',
        'Vocabulary': 'fas fa-language', 
        'Exercise': 'fas fa-pencil-alt',
        'Test': 'fas fa-quiz',
        'Speaking': 'fas fa-microphone',
        'Grammar': 'fas fa-spell-check',
        'Listening': 'fas fa-headphones',
        'Reading': 'fas fa-book-reader',
        'Writing': 'fas fa-pen'
    }
    return icon_map.get(content_type, 'fas fa-file')

@register.filter 
def progress_color(progress):
    """
    Return a progress bar color based on completion percentage.
    Usage: {{ lesson.progress|progress_color }}
    """
    progress = int(progress or 0)
    if progress >= 80:
        return 'success'
    elif progress >= 50:
        return 'warning'
    elif progress > 0:
        return 'info'
    else:
        return 'secondary'

@register.filter
def duration_format(minutes):
    """
    Format duration in minutes to a human readable format.
    Usage: {{ lesson.estimated_duration|duration_format }}
    """
    if not minutes:
        return "0 min"
    
    minutes = int(minutes)
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}min"

@register.simple_tag
def progress_ring(percentage, size=60):
    """
    Generate an SVG progress ring.
    Usage: {% progress_ring lesson.progress 80 %}
    """
    percentage = int(percentage or 0)
    radius = (size - 10) // 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    
    svg = f'''
    <svg width="{size}" height="{size}" class="progress-ring">
        <circle cx="{size//2}" cy="{size//2}" r="{radius}" 
                stroke="#e9ecef" stroke-width="4" fill="none"/>
        <circle cx="{size//2}" cy="{size//2}" r="{radius}" 
                stroke="#007bff" stroke-width="4" fill="none"
                stroke-dasharray="{circumference}" 
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                transform="rotate(-90 {size//2} {size//2})"/>
        <text x="{size//2}" y="{size//2}" text-anchor="middle" 
              dy="0.3em" font-size="{size//5}" font-weight="bold">
            {percentage}%
        </text>
    </svg>
    '''
    return mark_safe(svg)

@register.inclusion_tag('course/learning/components/lesson_status_badge.html')
def lesson_status_badge(lesson):
    """
    Render a lesson status badge.
    Usage: {% lesson_status_badge lesson %}
    """
    return {'lesson': lesson}

@register.inclusion_tag('course/learning/components/unit_progress_card.html')  
def unit_progress_card(unit):
    """
    Render a unit progress card.
    Usage: {% unit_progress_card unit %}
    """
    return {'unit': unit}

@register.filter
def multiply(value, arg):
    """
    Multiply two values.
    Usage: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """
    Subtract arg from value.
    Usage: {{ value|subtract:arg }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    Calculate percentage.
    Usage: {{ completed|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0