from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Curso, InscripcionCurso
from .serializers import CursoSerializer, InscripcionCursoSerializer


def paginar_cursos(queryset, page_number):
    paginator = Paginator(queryset, 5)
    page = paginator.get_page(page_number)

    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': CursoSerializer(page.object_list, many=True).data
    })



@api_view(['GET', 'POST'])
def cursos_api(request):

    if request.method == 'GET':
        cursos = Curso.objects.all().order_by('id')
        estado = request.query_params.get('estado')
        modalidad = request.query_params.get('modalidad')

        if estado:
            cursos = cursos.filter(estado=estado.upper())

        if modalidad:
            cursos = cursos.filter(modalidad=modalidad.upper())

        return paginar_cursos(
            cursos,
            request.query_params.get('page', 1)
        )

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {'detail': 'Se requiere administrador.'},
            status=403
        )

    if not request.user.has_perm('cursos.add_curso'):
        return Response({'detail': 'No tiene permisos para agregar cursos.'}, status=status.HTTP_403_FORBIDDEN)
    

    serializer = CursoSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def curso_detalle_api(request, id):

    try:
        curso = Curso.objects.get(id=id)
    except Curso.DoesNotExist:
        return Response(
            {'error': 'Curso no encontrado.'},
            status=404
        )

    if request.method == 'GET':
        return Response(CursoSerializer(curso).data)

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {'detail': 'Se requiere administrador.'},
            status=403
        )

    if request.method in ['PUT', 'PATCH']:

        if not request.user.has_perm('cursos.change_curso'):
            return Response({'detail': 'No tiene permisos para modificar cursos.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CursoSerializer(
            curso,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if not request.user.has_perm('cursos.delete_curso'):
        return Response({'detail': 'No tiene permisos para eliminar cursos.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        curso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar un curso con inscripciones.'},
            status=400
        )


@api_view(['GET', 'POST'])
def inscripciones_curso_api(request, id):

    try:
        curso = Curso.objects.get(id=id)
    except Curso.DoesNotExist:
        return Response(
            {'error': 'Curso no encontrado.'},
            status=404
        )

    if request.method == 'GET':
        inscripciones = curso.inscripciones.select_related(
            'cliente'
        ).order_by('fecha_inscripcion')

        return Response(
            InscripcionCursoSerializer(inscripciones, many=True).data,
            status=status.HTTP_200_OK
        )

    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Debe autenticarse para registrar una inscripción.'},
            status=401
        )

    if not request.user.has_perm('cursos.add_inscripcioncurso'):
        return Response({'detail': 'No tiene permisos para crear inscripciones.'}, status=status.HTTP_403_FORBIDDEN)
    
    
    with transaction.atomic():

        curso = Curso.objects.select_for_update().get(id=id)

        data = request.data.copy()
        data['curso'] = curso.id

        serializer = InscripcionCursoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def inscripcion_detalle_api(request, id):

    try:
        inscripcion = InscripcionCurso.objects.select_related(
            'cliente', 'curso'
        ).get(id=id)

    except InscripcionCurso.DoesNotExist:
        return Response(
            {'error': 'Inscripción no encontrada.'},
            status=404
        )
    
    if request.method == 'GET':
        return Response(InscripcionCursoSerializer(inscripcion).data)

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {'detail': 'Se requiere administrador.'},
            status=403
        )


    if request.method in ['PUT', 'PATCH']:
        if not request.user.has_perm('cursos.change_inscripcioncurso'):
            return Response({'detail': 'No tiene permisos para modificar inscripciones.'}, status=status.HTTP_403_FORBIDDEN)
            

        with transaction.atomic():
            curso_id = request.data.get('curso', inscripcion.curso_id)

            try:
                Curso.objects.select_for_update().get(id=curso_id)
            except (Curso.DoesNotExist, ValueError, TypeError):
                return Response(
                    {'curso': 'Curso no encontrado.'},
                    status=400
                )

            serializer = InscripcionCursoSerializer(
                inscripcion,
                data=request.data,
                partial=request.method == 'PATCH'
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=400)

    if not request.user.has_perm('cursos.delete_inscripcioncurso'):
        return Response({'detail': 'No tiene permisos para eliminar inscripciones.'}, status=status.HTTP_403_FORBIDDEN)
        
    inscripcion.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
def estadisticas_cursos_api(request):

    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Autenticación requerida.'},
            status=401
        )

    if not request.user.is_staff:
        return Response(
            {'detail': 'Se requiere administrador.'},
            status=403
        )

    mayor = Curso.objects.annotate(
        participantes=Count(
            'inscripciones',
            filter=Q(inscripciones__estado='inscrita')
        )
    ).order_by('-participantes', 'nombre').first()

    curso_mayor = None

    if mayor:
        curso_mayor = {
            'id': mayor.id,
            'nombre': mayor.nombre,
            'participantes': mayor.participantes
        }

    return Response({
        'cursos_programados': Curso.objects.filter(
            estado='PROGRAMADO'
        ).count(),
        'cursos_virtuales': Curso.objects.filter(
            modalidad='VIRTUAL'
        ).count(),
        'cursos_presenciales': Curso.objects.filter(
            modalidad='PRESENCIAL'
        ).count(),
        'inscripciones_activas': InscripcionCurso.objects.filter(
            estado='inscrita'
        ).count(),
        'curso_mayor_participacion': curso_mayor
    })