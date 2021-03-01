"""OPRF service request handler and request construction client.

Oblivious pseudo-random function (OPRF) service request handler
(that serves as an endpoint for the service) and client request
construction class (to help clients build requests concisely).
"""

from __future__ import annotations
from typing import Union
import doctest
import base64
import json
import bcl
import oprf

def key() -> bytes:
    """
    Create a secret/private key to be maintained by the service.
    """
    return bcl.symmetric.secret()

def key_base64() -> bytes:
    """
    Create a secret/private key to be maintained by the service.
    """
    return base64.standard_b64encode(bcl.symmetric.secret()).decode('utf-8')

def mask(k: bytes, m: oprf.mask = None, d: oprf.data = None) -> Union[oprf.mask, oprf.data]:
    """
    Function implementing service: returns a new encrypted mask if no
    mask or data is supplied, or applies the decrypted mask if both are
    supplied.
    """
    # If no mask is supplied, return a new encrypted mask.
    if m is None:
        return bcl.symmetric.encrypt(k, oprf.mask())

    # Return the masked data.
    return oprf.mask(bcl.symmetric.decrypt(k, m))(d)

def handler(k: bytes, request: Union[str, dict]) -> dict:
    """
    Wrapper for service function that accepts inputs as a JSON
    string or Python dictionary.
    """
    # Convert request to a dictionary if it is a JSON string.
    request = json.loads(request) if isinstance(request, str) else request

    # Convert the key from Base64 if it is a string.
    k = base64.standard_b64decode(k) if isinstance(k, str) else k

    # Extract arguments.
    m = oprf.mask.from_base64(request['mask'][0]) if 'mask' in request else None
    d = oprf.data.from_base64(request['data'][0]) if 'data' in request else None

    if m is None:
        return {
            'status': 'success',
            'mask': [base64.standard_b64encode(mask(k, m, d)).decode('utf-8')]
        }

    if m is not None and d is not None:
        return {
            'status': 'success',
            'data': [base64.standard_b64encode(mask(k, m, d)).decode('utf-8')]
        }

    return {'status': 'failure'}

if __name__ == "__main__":
    doctest.testmod()
