from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import (
    Grado, Materia, Estudiante, CategoriaNota, Nota,
    Asistencia, ReporteComportamiento, ActividadPendiente, PERIODOS
)

# ── helpers ──────────────────────────────────────
def _periodo(request, default=1):
    try:
        p = int(request.GET.get("periodo", default))
        return p if 1 <= p <= 4 else default
    except (TypeError, ValueError):
        return default


# ════════════════════════════════════════════════
#  GRADOS
# ════════════════════════════════════════════════
def grados(request):
    return render(request, "grados.html", {"grados": Grado.objects.all()})


def detalle_grado(request, id):
    grado = get_object_or_404(Grado, id=id)
    return render(request, "detalle_grado.html", {
        "grado": grado,
        "materias": grado.materias.all(),
        "estudiantes": grado.estudiantes.all(),
    })


# ════════════════════════════════════════════════
#  FOTO ESTUDIANTE
# ════════════════════════════════════════════════
@require_POST
def subir_foto_estudiante(request, est_id):
    est = get_object_or_404(Estudiante, id=est_id)
    if "foto" not in request.FILES:
        return JsonResponse({"ok": False, "error": "No se recibió archivo"}, status=400)
    if est.foto:
        try:
            est.foto.delete(save=False)
        except Exception:
            pass
    est.foto = request.FILES["foto"]
    est.save()
    return JsonResponse({"ok": True, "url": est.foto.url})


# ════════════════════════════════════════════════
#  NOTAS
# ════════════════════════════════════════════════
def detalle_materia(request, id):
    materia    = get_object_or_404(Materia, id=id)
    periodo    = _periodo(request)
    estudiantes = materia.grado.estudiantes.all()
    categorias  = materia.categorias.filter(periodo=periodo)

    datos = []
    for e in estudiantes:
        fila = []
        for c in categorias:
            nota = Nota.objects.filter(estudiante=e, categoria=c).first()
            if nota is None:
                nota = Nota.objects.create(estudiante=e, categoria=c, valor=None)
            fila.append(nota)
        datos.append({"estudiante": e, "notas": fila})

    return render(request, "detalle_materia.html", {
        "materia": materia,
        "categorias": categorias,
        "datos": datos,
        "total_porcentaje": sum(c.porcentaje for c in categorias),
        "periodo_actual": periodo,
        "periodos": PERIODOS,
    })


def agregar_categoria(request, id):
    materia = get_object_or_404(Materia, id=id)
    periodo = _periodo(request)
    total   = materia.categorias.filter(periodo=periodo).count()
    CategoriaNota.objects.create(
        materia=materia, periodo=periodo,
        nombre=f"Actividad {total+1}", porcentaje=10, orden=total
    )
    return redirect(f"/materia/{id}/?periodo={periodo}")


@require_POST
def eliminar_categoria(request, cat_id):
    cat = get_object_or_404(CategoriaNota, id=cat_id)
    cat.delete()
    return JsonResponse({"ok": True})


@require_POST
def actualizar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    try:
        data  = json.loads(request.body)
        valor = data.get("valor")
        if valor is None or valor == "":
            nota.valor = None
        else:
            nota.valor = max(20, min(100, int(valor)))
        nota.save()
        return JsonResponse({"ok": True})
    except (ValueError, KeyError):
        return JsonResponse({"ok": False}, status=400)


@require_POST
def actualizar_categoria(request, cat_id):
    cat = get_object_or_404(CategoriaNota, id=cat_id)
    try:
        data = json.loads(request.body)
        if "nombre"     in data: cat.nombre     = data["nombre"]
        if "porcentaje" in data: cat.porcentaje = max(0, min(100, int(data["porcentaje"])))
        cat.save()
        return JsonResponse({"ok": True})
    except (ValueError, KeyError):
        return JsonResponse({"ok": False}, status=400)


# ════════════════════════════════════════════════
#  ASISTENCIA
# ════════════════════════════════════════════════
def asistencia_materia(request, materia_id):
    materia     = get_object_or_404(Materia, id=materia_id)
    periodo     = _periodo(request)
    estudiantes = materia.grado.estudiantes.all()
    return render(request, "asistencia.html", {
        "materia": materia,
        "estudiantes": estudiantes,
        "periodo_actual": periodo,
        "periodos": PERIODOS,
    })


def asistencia_api(request, materia_id):
    materia     = get_object_or_404(Materia, id=materia_id)
    estudiantes = materia.grado.estudiantes.all()
    periodo     = _periodo(request)

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        if fecha:
            for e in estudiantes:
                estado = request.POST.get(f"estado_{e.id}", "P")
                Asistencia.objects.update_or_create(
                    materia=materia, estudiante=e, periodo=periodo, fecha=fecha,
                    defaults={"estado": estado}
                )
        return JsonResponse({"ok": True})

    fecha = request.GET.get("fecha", "")
    asistencias = {}
    if fecha:
        for a in Asistencia.objects.filter(materia=materia, periodo=periodo, fecha=fecha):
            asistencias[a.estudiante_id] = a.estado

    datos = [{"id": e.id, "nombre": e.nombre, "estado": asistencias.get(e.id, "P")} for e in estudiantes]
    return JsonResponse({"estudiantes": datos, "fecha": fecha})


def historial_asistencia(request, materia_id):
    materia     = get_object_or_404(Materia, id=materia_id)
    periodo     = _periodo(request)
    estudiantes = list(materia.grado.estudiantes.values("id", "nombre"))
    qs          = Asistencia.objects.filter(materia=materia, periodo=periodo)
    fechas      = [str(f) for f in qs.values_list("fecha", flat=True).distinct().order_by("fecha")]

    tabla = {}
    for a in qs.select_related("estudiante"):
        tabla.setdefault(str(a.fecha), {})[a.estudiante_id] = a.estado

    return JsonResponse({"estudiantes": estudiantes, "fechas": fechas, "tabla": tabla})


# ════════════════════════════════════════════════
#  COMPORTAMIENTO
# ════════════════════════════════════════════════
def comportamiento_materia(request, materia_id):
    materia     = get_object_or_404(Materia, id=materia_id)
    periodo     = _periodo(request)
    estudiantes = materia.grado.estudiantes.all()
    reportes    = ReporteComportamiento.objects.filter(
        materia=materia, periodo=periodo
    ).select_related("estudiante")
    return render(request, "comportamiento.html", {
        "materia":     materia,
        "estudiantes": estudiantes,
        "reportes":    reportes,
        "tipos_falta": ReporteComportamiento.TIPOS_FALTA,
        "periodo_actual": periodo,
        "periodos":    PERIODOS,
    })


@require_POST
def crear_reporte(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    try:
        data    = json.loads(request.body)
        periodo = int(data.get("periodo", 1))
        est     = get_object_or_404(Estudiante, id=data["estudiante_id"])
        r = ReporteComportamiento.objects.create(
            materia=materia, estudiante=est, periodo=periodo,
            fecha=data["fecha"], tipo_falta=data["tipo_falta"],
            descripcion=data["descripcion"],
        )
        return JsonResponse({"ok": True, "id": r.id})
    except (KeyError, ValueError) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@require_POST
def eliminar_reporte(request, rep_id):
    get_object_or_404(ReporteComportamiento, id=rep_id).delete()
    return JsonResponse({"ok": True})


# ════════════════════════════════════════════════
#  ACTIVIDADES
# ════════════════════════════════════════════════
def actividades_materia(request, materia_id):
    materia    = get_object_or_404(Materia, id=materia_id)
    periodo    = _periodo(request)
    actividades = ActividadPendiente.objects.filter(materia=materia, periodo=periodo)
    return render(request, "actividades.html", {
        "materia":        materia,
        "actividades":    actividades,
        "estados":        ActividadPendiente.ESTADOS,
        "periodo_actual": periodo,
        "periodos":       PERIODOS,
    })


@require_POST
def crear_actividad(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    try:
        data    = json.loads(request.body)
        periodo = int(data.get("periodo", 1))
        a = ActividadPendiente.objects.create(
            materia=materia, periodo=periodo,
            titulo=data["titulo"],
            descripcion=data.get("descripcion", ""),
            fecha_entrega=data["fecha_entrega"],
            estado=data.get("estado", "pendiente"),
        )
        return JsonResponse({"ok": True, "id": a.id})
    except (KeyError, ValueError) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@require_POST
def actualizar_actividad(request, act_id):
    act = get_object_or_404(ActividadPendiente, id=act_id)
    try:
        data = json.loads(request.body)
        for field in ("titulo", "descripcion", "fecha_entrega", "estado"):
            if field in data:
                setattr(act, field, data[field])
        act.save()
        return JsonResponse({"ok": True})
    except (KeyError, ValueError) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@require_POST
def eliminar_actividad(request, act_id):
    get_object_or_404(ActividadPendiente, id=act_id).delete()
    return JsonResponse({"ok": True})