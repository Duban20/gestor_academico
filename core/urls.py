from django.urls import path
from .views import *

urlpatterns = [

    # Grados
    path('', grados, name='grados'),
    path('grado/<int:id>/', detalle_grado, name='detalle_grado'),

    # Notas
    path('materia/<int:id>/', detalle_materia, name='detalle_materia'),
    path('materia/<int:id>/agregar-categoria/', agregar_categoria, name='agregar_categoria'),
    path('nota/<int:nota_id>/actualizar/', actualizar_nota, name='actualizar_nota'),
    path('categoria/<int:cat_id>/actualizar/', actualizar_categoria, name='actualizar_categoria'),
    path('categoria/<int:cat_id>/eliminar/', eliminar_categoria, name='eliminar_categoria'),

    # Foto estudiante
    path('estudiante/<int:est_id>/foto/', subir_foto_estudiante, name='subir_foto_estudiante'),
    path('estudiante/<int:est_id>/toggle-activo/', toggle_activo, name='toggle_activo'),
    path('estudiante/<int:est_id>/toggle-participativo/', toggle_participativo, name='toggle_participativo'),

    # Asistencia
    path('materia/<int:materia_id>/exportar/', exportar_excel, name='exportar_excel'),

    path('materia/<int:materia_id>/asistencia/', asistencia_materia, name='asistencia_materia'),
    path('materia/<int:materia_id>/asistencia/api/', asistencia_api, name='asistencia_api'),
    path('materia/<int:materia_id>/asistencia/historial/', historial_asistencia, name='historial_asistencia'),

    # Comportamiento
    path('materia/<int:materia_id>/comportamiento/', comportamiento_materia, name='comportamiento_materia'),
    path('materia/<int:materia_id>/comportamiento/crear/', crear_reporte, name='crear_reporte'),
    path('reporte/<int:rep_id>/eliminar/', eliminar_reporte, name='eliminar_reporte'),

    # Actividades pendientes
    path('materia/<int:materia_id>/actividades/', actividades_materia, name='actividades_materia'),
    path('materia/<int:materia_id>/actividades/crear/', crear_actividad, name='crear_actividad'),
    path('actividad/<int:act_id>/actualizar/', actualizar_actividad, name='actualizar_actividad'),
    path('actividad/<int:act_id>/eliminar/', eliminar_actividad, name='eliminar_actividad'),
]