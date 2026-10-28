from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteSerializer


def respuesta_paginada(queryset, serializer_class, page_number):
    paginator = Paginator(queryset, 5)
    page = paginator.get_page(page_number)
    serializer = serializer_class(page.object_list, many=True)
    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': serializer.data
    })

@api_view(['GET', 'POST'])
def clientes_api(request):
    if request.method == 'GET':
        clientes = Cliente.objects.order_by('id')
        activo = request.query_params.get('activo')
        buscar = request.query_params.get('buscar')

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            clientes = clientes.filter(activo=activo.lower() == 'true')
        if buscar:
            clientes = clientes.filter(
                nombre__icontains=buscar
            ) | clientes.filter(
                cedula__icontains=buscar
            )

        return respuesta_paginada(
            clientes, ClienteSerializer,
            request.query_params.get('page', 1)
        )


    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=status.HTTP_403_FORBIDDEN)
    
    if not request.user.has_perm('clientes.add_cliente'):
        return Response({'detail': 'No tiene permisos para agregar clientes.'}, status=status.HTTP_403_FORBIDDEN)


    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def cliente_detalle_api(request, pk):
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return Response({'error': 'Cliente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ClienteSerializer(cliente).data)

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'detail': 'Se requiere administrador.'}, status=status.HTTP_403_FORBIDDEN)


    if request.method in ['PUT', 'PATCH']:
        if not request.user.has_perm('clientes.change_cliente'):
            return Response({'detail': 'No tiene permisos para modificar clientes.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClienteSerializer(
            cliente, data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    if not request.user.has_perm('clientes.delete_cliente'):
        return Response({'detail': 'No tiene permisos para eliminar clientes.'}, status=status.HTTP_403_FORBIDDEN)
    
    cliente.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)