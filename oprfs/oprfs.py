"""
Easy-to-deploy oblivious pseudo-random function (OPRF) service that allows
other parties (typically participants in some secure multi-party computation
protocol) to obtain a persistent mask which they cannot decrypt but which they
can safely apply (via requests to the service) to private data values of their
choice.

This module includes an OPRF service request handler (that serves as an
endpoint for the service) and client request construction class (to help
clients build requests concisely).
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

    >>> len(key())
    32
    """
    return bcl.symmetric.secret()

def key_base64() -> str:
    """
    Create a secret/private key to be maintained by the service.

    >>> len(base64.standard_b64decode(key_base64()))
    32
    """
    return base64.standard_b64encode(bcl.symmetric.secret()).decode('utf-8')

def mask(k: bytes, m: oprf.mask = None, d: oprf.data = None) -> Union[oprf.mask, oprf.data]:
    """
    Function implementing service: returns a new encrypted mask if no
    mask or data is supplied, or applies the decrypted mask if both are
    supplied.

    >>> k = key()
    >>> m = mask(k)
    >>> d = oprf.data.hash('abc')
    >>> mask(k, m, d) == oprf.mask(bcl.symmetric.decrypt(k, m))(d)
    True
    """
    # If no mask is supplied, return a new encrypted mask.
    if m is None:
        return bcl.symmetric.encrypt(k, oprf.mask())

    # Return the masked data.
    return oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)

def handler(k: bytes, request: Union[str, dict]) -> dict:
    """
    Wrapper for service function that accepts inputs as a JSON
    string or Python dictionary.

    >>> k = key()
    >>> r = handler(k, {})
    >>> r['status'] == 'success'
    True
    >>> r = handler(k, '{}')
    >>> r['status'] == 'success'
    True
    >>> m = oprf.mask.from_base64(r['mask'][0])
    >>> d = oprf.data.hash('abc')
    >>> mask(k, m, d) == oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)
    True
    >>> r = handler(k, {'mask': [m.to_base64()], 'data': [d.to_base64()]})
    >>> r['status'] == 'success'
    True
    >>> (m_str, d_str) = (str(m.to_base64()), str(d.to_base64()))
    >>> s = '{"mask": ["' + m_str + '"], "data": ["' + d_str + '"]}'
    >>> r = handler(k, s)
    >>> r['status'] == 'success'
    True
    >>> oprf.data.from_base64(r['data'][0]) == oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)
    True
    >>> r = handler(k, {'mask': [m.to_base64()]})
    >>> r['status']
    'failure'
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

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
