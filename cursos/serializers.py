from rest_framework import serializers
from .models import Curso, InscripcionCurso


class CursoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Curso
        fields = '__all__'
        read_only_fields = []


    def validate(self, data):
        precio = data.get('precio')
        cupo = data.get('cupo_maximo')
        duracion = data.get('duracion_horas')

        if precio is not None and precio <= 0:
            raise serializers.ValidationError({
                'precio': 'El precio debe ser mayor que cero.'
            })

        if cupo is not None and cupo <= 0:
            raise serializers.ValidationError({
                'cupo_maximo': 'El cupo debe ser mayor que cero.'
            })

        if duracion is not None and duracion <= 0:
            raise serializers.ValidationError({
                'duracion_horas': 'La duración debe ser mayor que cero.'
            })

        if self.instance and cupo is not None:
            inscritos = self.instance.inscripciones.filter(
                estado='inscrita'
            ).count()

            if cupo < inscritos:
                raise serializers.ValidationError({
                    'cupo_maximo': 'No puede ser menor que las inscripciones actuales.'
                })

        return data


class InscripcionCursoSerializer(serializers.ModelSerializer):

    class Meta:
        model = InscripcionCurso
        fields = '__all__'

    def validate(self, data):
        curso = data.get('curso')
        cliente = data.get('cliente')
        estado = data.get('estado', 'inscrita')

        if curso is None or cliente is None:
            return data

        if estado == 'inscrita':
            if curso.estado != 'PROGRAMADO':
                raise serializers.ValidationError(
                    'Solo se permiten inscripciones en cursos programados.'
                )

            if not cliente.activo:
                raise serializers.ValidationError(
                    'El cliente debe estar activo.'
                )

            inscritos = InscripcionCurso.objects.filter(
                curso=curso,
                estado='inscrita'
            )

            if self.instance:
                inscritos = inscritos.exclude(pk=self.instance.pk)

            if inscritos.count() >= curso.cupo_maximo:
                raise serializers.ValidationError(
                    'El curso no tiene cupos disponibles.'
                )

        duplicado = InscripcionCurso.objects.filter(
            curso=curso,
            cliente=cliente
        )

        if self.instance:
            duplicado = duplicado.exclude(pk=self.instance.pk)

        if duplicado.exists():
            raise serializers.ValidationError(
                'El cliente ya tiene una inscripción en este curso.'
            )

        return data