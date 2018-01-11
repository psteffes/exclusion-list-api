from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ExcListUMIDSerializer, ExcListKeySerializer
from .exc_list_manager import ExcList, ExcListError
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def find_umid(request):
    """
    API endpoint that searches the exclusion list for the provided key and umid
    Returns the entry as a json string if a match is found
    """
    try:
        logger.info('<RESTRequest: {} \'{}\' data={}>'.format(request.method, request.path, request.data))
        serializer = ExcListUMIDSerializer(data=request.data)

        if serializer.is_valid():
            result = ExcList().find_umid(serializer.data['umid'])
            # Return 200 on a successful match
            response = Response(result)
        else:
            # Return a 400 on invalid input
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Return a 404 on a failed match
    except ExcListError as e:
        response = Response({
            "message": e.message,
            "status": 404,
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Return a 500 on any unexpected exceptions
    except Exception as e:    # pragma: no cover
        response = Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info('Return status_code={} response={}'.format(response.status_code, response.data))
    return response


@api_view(['POST'])
def find_key(request):
    """
    API endpoint that searches the exclusion list for the provided key and umid
    Returns the entry as a json string if a match is found
    """
    try:
        logger.info('<RESTRequest: {} \'{}\' data={}>'.format(request.method, request.path, request.data))
        serializer = ExcListKeySerializer(data=request.data)

        if serializer.is_valid():
            #result = exc_list_find(serializer.data)
            result = ExcList().find_key(serializer.data['key'])
            # Return 200 on a successful match
            response = Response(result)
        else:
            # Return a 400 on invalid input
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Return a 404 on a failed match
    except ExcListError as e:
        response = Response({
            "message": e.message,
            "status": 404,
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Return a 500 on any unexpected exceptions
    except Exception as e:    # pragma: no cover
        response = Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info('Return status_code={} response={}'.format(response.status_code, response.data))
    return response


@api_view(['POST'])
def add_key(request):
    """
    API endpoint that increments bad attempts for the provided key
    Will create the exc list entry if it does not exist
    Returns 200 on a successful add
    """
    try:
        logger.info('<RESTRequest: {} \'{}\' data={}>'.format(request.method, request.path, request.data))
        serializer = ExcListKeySerializer(data=request.data)

        if serializer.is_valid():
            result = ExcList().add_key(serializer.data['key'])
            # Return 200 on a successful add
            response = Response(result)
        else:
            # Return a 400 on invalid input
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Return a 500 on any unexpected exceptions
    except Exception as e:    # pragma: no cover
        response = Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info('Return status_code={} response={}'.format(response.status_code, response.data))
    return response


@api_view(['POST'])
def delete_key(request):
    """
    API endpoint that deletes the exc list entry for the provided key
    Returns 200 on a successful delete
    """
    try:
        logger.info('<RESTRequest: {} \'{}\' data={}>'.format(request.method, request.path, request.data))
        serializer = ExcListKeySerializer(data=request.data)

        if serializer.is_valid():
            result = ExcList().delete_key(serializer.data['key'])
            # Return 200 on a successful delete
            response = Response(result)
        else:
            # Return a 400 on invalid input
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Return a 500 on any unexpected exceptions
    except Exception as e:    # pragma: no cover
        response = Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info('Return status_code={} response={}'.format(response.status_code, response.data))
    return response

