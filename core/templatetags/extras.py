from django import template

register = template.Library()


@register.filter
def color_nota(valor):
    """Devuelve la clase CSS según el rango. Si valor es None devuelve ''."""
    if valor is None:
        return ''
    valor = int(valor)
    if valor <= 69: return "nota-bajo"
    if valor <= 79: return "nota-basico"
    if valor <= 89: return "nota-alto"
    return "nota-superior"


@register.filter
def badge_estado(e):
    return {
        "pendiente":  "badge-pendiente",
        "entregada":  "badge-entregada",
    }.get(e, "")