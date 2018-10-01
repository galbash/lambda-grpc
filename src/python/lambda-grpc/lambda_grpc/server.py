"""
Server-side related gRPC implementation
"""

import base64
import warnings

import google.rpc.code_pb2

from .error import RPCError, RPCWarning
from .lambda_rpc_pb2 import InvokeRequest, InvokeResponse


class InvalidAPIError(Exception):
    """
    An error that is raised when the given api is not a valid gRPC API class
    """
    pass


def implements(request_type, response_type):
    """
    A decorator for making an AWS Lambda implement a gRPC server
    :param request_type: The expected request type
    :param response_type: The expected response type
    :return: The decorated function
    """
    # TODO: add api validation

    def _implements(wrapped):
        def wrapper(event, context):
            request = InvokeRequest.FromString(
                base64.b64decode(event)
            )

            client_request = request_type()
            request.client_request.Unpack(client_request)
            response = InvokeResponse()
            try:
                client_response = wrapped(client_request, context)
                if response:
                    response.client_response.Pack(client_response)

                if type(response) is not response_type:
                    warnings.warn(RPCWarning('response type is different then expected'))

                response.status.code = google.rpc.code_pb2.OK

            except RPCError as rpc_error:
                response.status.code = rpc_error.code
                response.status.message = rpc_error.message

            except Exception as error:
                response.status.code = google.rpc.code_pb2.INTERNAL
                response.status.message = error.message

            return base64.b64encode(response.SerializeToString()).decode('utf-8')

        return wrapper
    return _implements
