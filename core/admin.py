from django.contrib import admin
from .models import *

admin.site.register(Grado)
admin.site.register(Estudiante)
admin.site.register(Materia)
admin.site.register(CategoriaNota)
admin.site.register(Nota)
admin.site.register(Asistencia)