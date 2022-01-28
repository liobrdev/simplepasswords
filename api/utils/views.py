from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE',])
def not_found(request, exception=None):
    return Response({ 'detail': 'Not found.' }, status=HTTP_404_NOT_FOUND)