from django.contrib import admin
from .models import Curso
from .models import InscripcionCurso

admin.site.register(Curso)
admin.site.register(InscripcionCurso)