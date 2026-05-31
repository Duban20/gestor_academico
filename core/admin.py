from django.contrib import admin
from django.utils.html import format_html
from .models import Grado, Estudiante, Materia, CategoriaNota, Nota, Asistencia


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "descripcion", "total_estudiantes", "total_materias")
    search_fields = ("nombre",)

    def total_estudiantes(self, obj):
        return obj.estudiantes.count()
    total_estudiantes.short_description = "Estudiantes"

    def total_materias(self, obj):
        return obj.materias.count()
    total_materias.short_description = "Materias"


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display  = ("nombre_display", "codigo", "grado", "estado_badge", "participativo_badge")
    list_filter   = ("grado", "activo", "participativo")
    search_fields = ("nombre", "codigo")
    ordering      = ("grado", "nombre")

    fieldsets = (
        ("Información básica", {
            "fields": ("grado", "nombre", "codigo", "foto")
        }),
        ("Estado del estudiante", {
            "fields": ("activo", "razon_inactivo"),
            "description": (
                "Si el estudiante deja de asistir, desmarca 'Activo' y escribe "
                "la razón. Sus notas quedarán bloqueadas."
            ),
        }),
        ("Participación", {
            "fields": ("participativo",),
        }),
    )

    def nombre_display(self, obj):
        if not obj.activo:
            return format_html(
                '<span style="color:#b91c1c;text-decoration:line-through;">{}</span> '
                '<span style="background:#fff0f0;color:#b91c1c;padding:2px 6px;'
                'border-radius:4px;font-size:11px;font-weight:600;">INACTIVO</span>',
                obj.nombre
            )
        if obj.participativo:
            return format_html(
                '{} <span style="color:#f59e0b;" title="Estudiante participativo">★</span>',
                obj.nombre
            )
        return obj.nombre
    nombre_display.short_description = "Nombre"
    nombre_display.admin_order_field = "nombre"

    def estado_badge(self, obj):
        if obj.activo:
            return format_html(
                '<span style="background:#f0fdf4;color:#15803d;padding:2px 8px;'
                'border-radius:4px;font-size:11px;font-weight:600;">Activo</span>'
            )
        return format_html(
            '<span style="background:#fff0f0;color:#b91c1c;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;" title="{}">'
            'Inactivo</span>',
            obj.razon_inactivo or "Sin razón registrada"
        )
    estado_badge.short_description = "Estado"

    def participativo_badge(self, obj):
        if obj.participativo:
            return format_html('<span style="color:#f59e0b;font-size:16px;">★</span>')
        return format_html('<span style="color:#e5e7eb;font-size:16px;">☆</span>')
    participativo_badge.short_description = "★"


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "grado")
    list_filter   = ("grado",)
    search_fields = ("nombre",)


@admin.register(CategoriaNota)
class CategoriaNota_Admin(admin.ModelAdmin):
    list_display  = ("nombre", "descripcion", "materia", "periodo", "porcentaje", "orden")
    list_filter   = ("materia__grado", "periodo")
    search_fields = ("nombre", "materia__nombre")


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display  = ("estudiante", "categoria", "valor")
    list_filter   = ("categoria__materia__grado", "categoria__periodo")
    search_fields = ("estudiante__nombre",)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display  = ("estudiante", "materia", "periodo", "fecha", "estado")
    list_filter   = ("materia__grado", "periodo", "estado")
    search_fields = ("estudiante__nombre",)
    date_hierarchy = "fecha"