from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from productos.models import Producto
from cursos.models import Curso, InscripcionCurso

from .models import Factura, DetalleFactura
from .serializers import FacturaSerializer, DetalleFacturaSerializer


def paginar_facturas(queryset, page_number):
    paginator = Paginator(queryset, 5)
    page = paginator.get_page(page_number)

    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': FacturaSerializer(page.object_list, many=True).data
    })


@api_view(['GET', 'POST'])
def facturas_api(request):

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

    if not request.user.has_perm('facturas.add_factura'):
        return Response({'detail': 'No tiene permisos para agregar una factura.'}, status=status.HTTP_403_FORBIDDEN)
    

    if request.method == 'GET':
        facturas = Factura.objects.select_related(
            'cliente'
        ).order_by('id')

        estado = request.query_params.get('estado')
        cliente = request.query_params.get('cliente')

        if estado:
            facturas = facturas.filter(estado=estado.upper())

        if cliente:
            facturas = facturas.filter(cliente_id=cliente)

        return paginar_facturas(
            facturas,
            request.query_params.get('page', 1)
        )

    data = request.data.copy()
    data['total'] = '0.00'
    if data.get('estado') not in ['PENDIENTE', 'PAGADA', 'CANCELADA']:
        data['estado'] = 'PENDIENTE'

    serializer = FacturaSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def factura_detalle_api(request, id):

    if not request.user.is_authenticated:
        return Response({'detail': 'Autenticación requerida.'}, status=401)

    if not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=403)

    try:
        factura = Factura.objects.get(id=id)
    except Factura.DoesNotExist:
        return Response({'error': 'Factura no encontrada.'}, status=404)

    if request.method == 'GET':
        return Response(FacturaSerializer(factura).data)

    if request.method in ['PUT', 'PATCH']:

        if not request.user.has_perm('facturas.change_factura'):
            return Response({'detail': 'No tiene permisos para modificar una factura.'}, status=status.HTTP_403_FORBIDDEN)

        if factura.estado == 'CANCELADA':
            return Response(
                {'error': 'No se pueden modificar facturas canceladas.'},
                status=400
            )

        data = request.data.copy()

        if 'cliente' in data and str(data['cliente']) != str(factura.cliente_id):
            return Response(
                {'error': 'No puede cambiar el cliente de la factura.'},
                status=400
            )

        estado_nuevo = data.get('estado', factura.estado)

        if estado_nuevo == 'CANCELADA' and factura.detalles.exists():
            return Response(
                {'error': 'Elimine los detalles antes de cancelar la factura.'},
                status=400
            )

        data['total'] = str(factura.total)

        serializer = FacturaSerializer(
            factura,
            data=data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    if factura.estado != 'PENDIENTE' or factura.detalles.exists():
        return Response(
            {'error': 'Solo puede eliminar facturas pendientes sin detalles.'},
            status=400
        )

    if not request.user.has_perm('facturas.delete_factura'):
        return Response({'detail': 'No tiene permisos para eliminar una factura.'}, status=status.HTTP_403_FORBIDDEN)
    factura.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def detalles_factura_api(request, id):

    if not request.user.is_authenticated:
        return Response({'detail': 'Autenticación requerida.'}, status=401)

    if not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=403)

    if not request.user.has_perm('facturas.add_detallefactura'):
        return Response({'detail': 'No tiene permisos para agregar un detalle factura.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        factura = Factura.objects.get(id=id)
    except Factura.DoesNotExist:
        return Response({'error': 'Factura no encontrada.'}, status=404)

    if request.method == 'GET':
        detalles = factura.detalles.select_related(
            'producto', 'curso'
        ).order_by('id')

        return Response(
            DetalleFacturaSerializer(detalles, many=True).data
        )

    with transaction.atomic():

        factura = Factura.objects.select_for_update().get(id=id)

        if factura.estado == 'CANCELADA':
            return Response(
                {'error': 'No se agregan detalles a facturas canceladas.'},
                status=400
            )

        data = request.data.copy()
        data['factura'] = factura.id

        serializer = DetalleFacturaSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        producto = serializer.validated_data.get('producto')
        curso = serializer.validated_data.get('curso')
        cantidad = serializer.validated_data.get('cantidad', 1)

        if bool(producto) == bool(curso):
            return Response(
                {'error': 'Seleccione un producto o un curso, no ambos.'},
                status=400
            )

        if producto:
            producto = Producto.objects.select_for_update().get(id=producto.id)

            if not producto.activo or producto.stock < cantidad:
                return Response(
                    {'error': 'Producto inactivo o stock insuficiente.'},
                    status=400
                )

            precio = producto.precio
        else:
            curso = Curso.objects.select_for_update().get(id=curso.id)

            if cantidad != 1 or curso.estado != 'PROGRAMADO':
                return Response(
                    {'error': 'Curso no disponible o cantidad incorrecta.'},
                    status=400
                )

            if not InscripcionCurso.objects.filter(
                curso=curso,
                cliente=factura.cliente,
                estado='inscrita'
            ).exists():
                return Response(
                    {'error': 'El cliente debe estar inscrito en el curso.'},
                    status=400
                )

            if DetalleFactura.objects.filter(
                factura__cliente=factura.cliente,
                curso=curso
            ).exclude(
                factura__estado='CANCELADA'
            ).exists():
                return Response(
                    {'error': 'Este curso ya está facturado para el cliente.'},
                    status=400
                )

            precio = curso.precio


        try:
            detalle = serializer.save()
        except ValidationError as error:
            return Response({'error': error.messages}, status=400)

        return Response(
            DetalleFacturaSerializer(detalle).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'DELETE'])
def detalle_factura_api(request, id):

    if not request.user.is_authenticated:
        return Response({'detail': 'Autenticación requerida.'}, status=401)

    if not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=403)

    if not request.user.has_perm('facturas.delete_detallefactura'):
            return Response({'detail': 'No tiene permisos para eliminar un detallefactura.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        detalle = DetalleFactura.objects.get(id=id)
    except DetalleFactura.DoesNotExist:
        return Response({'error': 'Detalle no encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(DetalleFacturaSerializer(detalle).data)

    with transaction.atomic():

        factura = Factura.objects.select_for_update().get(
            id=detalle.factura_id
        )

        if factura.estado != 'PENDIENTE':
            return Response(
                {'error': 'No puede eliminar detalles de una factura cerrada.'},
                status=400
            )

        try:
            detalle.delete()
        except ValidationError as error:
            return Response({'error': error.messages}, status=400)

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def estadisticas_facturacion_api(request):

    if not request.user.is_authenticated:
        return Response({'detail': 'Autenticación requerida.'}, status=401)

    if not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=403)

    ingresos = Factura.objects.filter(
        estado='PAGADA'
    ).aggregate(total=Sum('total'))['total']

    mayor = Factura.objects.annotate(
        cantidad_detalles=Count('detalles')
    ).order_by('-cantidad_detalles', 'id').first()

    factura_mayor = None

    if mayor:
        factura_mayor = {
            'id': mayor.id,
            'cantidad_detalles': mayor.cantidad_detalles
        }

    return Response({
        'facturas_pendientes': Factura.objects.filter(
            estado='PENDIENTE'
        ).count(),
        'facturas_pagadas': Factura.objects.filter(
            estado='PAGADA'
        ).count(),
        'facturas_canceladas': Factura.objects.filter(
            estado='CANCELADA'
        ).count(),
        'ingresos_totales': ingresos if ingresos is not None else 0,
        'factura_mas_detalles': factura_mayor
    })