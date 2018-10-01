"""
Server-side related gRPC implementation
"""
import json
import base64
import boto3
import grpc

import google.rpc.code_pb2
from .lambda_rpc_pb2 import InvokeRequest, InvokeResponse
from .error import RPCError


class AWSLambdaInvokeError(Exception):
    """
    An error that is raised when an AWS Lambda invocation fails
    """
    pass


_lambda_client_obj = None


def _lambda_client():
    global _lambda_client_obj
    if not _lambda_client_obj:
        _lambda_client_obj = boto3.client('lambda')
    return _lambda_client_obj


class _UnaryUnaryMultiCallable(object):
    """
    creates a unary unary operation against Lambda upon call
    """

    def __init__(self, channel, method, request_serializer, response_deserializer):
        self._channel = channel
        self._method = method
        self._request_serializer = request_serializer
        self._response_deserializer = response_deserializer

    def __call__(self, request, timeout=None, metadata=None, credentials=None):
        full_request = InvokeRequest()
        full_request.client_request.Pack(request)
        try:
            lambda_response = _lambda_client().invoke(
                FunctionName=self._channel._target,
                InvocationType='RequestResponse',
                Payload=json.dumps(
                    base64.b64encode(InvokeRequest.SerializeToString(full_request)).decode('utf-8')
                )
            )
        except Exception:
            raise AWSLambdaInvokeError('lambda {} invocation failed'.format(self._channel._target))

        if 'Payload' not in lambda_response:
            raise AWSLambdaInvokeError('Response Payload was not found')

        lambda_payload = lambda_response['Payload'].read()

        if 'FunctionError' in lambda_response:
            raise AWSLambdaInvokeError('The function errored with error: {}'.format(lambda_payload))

        response_payload = json.loads(lambda_payload)
        try:
            response = InvokeResponse.FromString(base64.b64decode(response_payload))
        except Exception:
            raise RPCError(
                code=google.rpc.code_pb2.UNKNOWN,
                message='Could not parse message from server. message: {}'.format(response_payload)
            )

        if not response.HasField('status') or not response.HasField('client_response'):
            raise RPCError(
                code=google.rpc.code_pb2.UNKNOWN,
                message='invalid response returned from Lambda'
            )

        if response.status.code != google.rpc.code_pb2.OK:
            raise RPCError(code=response.status.code, message=response.status.message)

        client_response = self._response_deserializer.__self__()
        response.client_response.Unpack(client_response)
        return client_response


class Channel(grpc.Channel):
    """
    A channel for gRPC operations to AWS Lambda server
    """

    def __init__(
        self,
        target,
    ):
        """
        :param target: The target function to invoke
        """
        self._target = target

    def subscribe(self, callback, try_to_connect=False):
        """
        Unused
        :param callback:
        :param try_to_connect:
        :return:
        """
        pass

    def unsubscribe(self, callback):
        """
        Unused
        :param callback:
        :return:
        """
        pass

    def unary_unary(self,
                    method,
                    request_serializer=None,
                    response_deserializer=None):
        return _UnaryUnaryMultiCallable(
            self,
            method,
            request_serializer,
            response_deserializer
        )

    def unary_stream(self,
                    method,
                    request_serializer=None,
                    response_deserializer=None):
        raise NotImplementedError()

    def stream_unary(self,
                     method,
                     request_serializer=None,
                     response_deserializer=None):
        raise NotImplementedError()

    def stream_stream(self,
                     method,
                     request_serializer=None,
                     response_deserializer=None):
        raise NotImplementedError()

    def close(self):
        pass







