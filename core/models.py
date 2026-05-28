from django.db import models


# ──────────────────────────────────────────────────
#  CONSTANTE PERIODOS (usada en todo el proyecto)
# ──────────────────────────────────────────────────
PERIODOS = [(1, "Periodo 1"), (2, "Periodo 2"), (3, "Periodo 3"), (4, "Periodo 4")]


class Grado(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    grado  = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="estudiantes")
    nombre = models.CharField(max_length=120)
    codigo = models.CharField(max_length=50, blank=True)
    foto   = models.ImageField(upload_to="estudiantes/", blank=True, null=True)

    def __str__(self):
        return self.nombre

    def iniciales(self):
        partes = self.nombre.strip().split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nombre[:2].upper()


class Materia(models.Model):
    grado  = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="materias")
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# ──────────────────────────────────────────────────
#  NOTAS  (por periodo)
# ──────────────────────────────────────────────────
class CategoriaNota(models.Model):
    materia    = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="categorias")
    periodo    = models.IntegerField(choices=PERIODOS, default=1)
    nombre     = models.CharField(max_length=100)
    porcentaje = models.IntegerField(default=100)
    orden      = models.IntegerField(default=0)

    class Meta:
        ordering = ["periodo", "orden"]


class Nota(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    categoria  = models.ForeignKey(CategoriaNota, on_delete=models.CASCADE)
    valor = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("estudiante", "categoria")


# ──────────────────────────────────────────────────
#  ASISTENCIA  (por periodo)
# ──────────────────────────────────────────────────
class Asistencia(models.Model):
    OPCIONES = [("P", "Presente"), ("A", "Ausente"), ("E", "Excusa")]

    materia    = models.ForeignKey(Materia, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    periodo    = models.IntegerField(choices=PERIODOS, default=1)
    fecha      = models.DateField()
    estado     = models.CharField(max_length=1, choices=OPCIONES)

    class Meta:
        unique_together = ("materia", "estudiante", "periodo", "fecha")


# ──────────────────────────────────────────────────
#  COMPORTAMIENTO  (por periodo)
# ──────────────────────────────────────────────────
class ReporteComportamiento(models.Model):
    TIPOS_FALTA = [
        ("irrespeto",    "Irrespeto al docente o compañeros"),
        ("bullying",     "Bullying / acoso"),
        ("indisciplina", "Indisciplina en clase"),
        ("trampa",       "Trampa / deshonestidad académica"),
        ("daño",         "Daño a propiedad"),
        ("lenguaje",     "Lenguaje inapropiado"),
        ("otro",         "Otro"),
    ]

    materia     = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="reportes")
    estudiante  = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="reportes")
    periodo     = models.IntegerField(choices=PERIODOS, default=1)
    fecha       = models.DateField()
    tipo_falta  = models.CharField(max_length=30, choices=TIPOS_FALTA)
    descripcion = models.TextField()
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]


# ──────────────────────────────────────────────────
#  ACTIVIDADES PENDIENTES  (por periodo)
# ──────────────────────────────────────────────────
class ActividadPendiente(models.Model):
    ESTADOS = [
        ("pendiente",  "Pendiente"),
        ("entregada",  "Entregada"),
    ]

    materia       = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="actividades")
    periodo       = models.IntegerField(choices=PERIODOS, default=1)
    titulo        = models.CharField(max_length=200)
    descripcion   = models.TextField(blank=True)
    fecha_entrega = models.DateField()
    estado        = models.CharField(max_length=15, choices=ESTADOS, default="pendiente")
    creado_en     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_entrega"]