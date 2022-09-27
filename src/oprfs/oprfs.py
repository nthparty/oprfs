"""
Easy-to-deploy oblivious
`pseudo-random function <https://en.wikipedia.org/wiki/Pseudorandom_function_family>`__
(OPRF) service that allows other parties (typically participants in some secure
multi-party computation protocol) to maintain a persistent mask which they
cannot decrypt but which they can safely apply (via requests to the service)
to private data values of their choice.

This module includes an OPRF service request handler (that serves as an
endpoint for the service and can be used in conjunction with libraries
such as `Flask <https://flask.palletsprojects.com>`__) and client request
construction class (to help clients build requests concisely).
"""
from __future__ import annotations
from typing import Union, Optional
import doctest
import base64
import json
import bcl
import oprf

def key() -> bcl.secret:
    """
    Create a :obj:`~bcl.bcl.secret` key to be maintained by the service.

    >>> len(key())
    32
    >>> isinstance(key(), bcl.secret)
    True
    """
    return bcl.symmetric.secret()

def key_base64() -> str:
    """
    Create a :obj:`~bcl.bcl.secret` key to be maintained by the service and return
    its Base64 UTF-8 string representation.

    >>> len(base64.standard_b64decode(key_base64()))
    32
    """
    return base64.standard_b64encode(bcl.symmetric.secret()).decode('utf-8')

def mask(
        k: bcl.secret,
        m: Optional[oprf.mask] = None,
        d: Optional[oprf.data] = None
    ) -> Union[oprf.mask, oprf.data]:
    """
    Function implementing a masking service. This function returns a new
    :obj:`~oprf.oprf.mask` object encrypted using the supplied
    :obj:`~bcl.bcl.secret` key (if no additional parameters are supplied), or
    decrypts and applies the supplied :obj:`~oprf.oprf.mask` to a
    :obj:`~oprf.oprf.data` object (if both an encrypted :obj:`~oprf.oprf.mask`
    object and a :obj:`~oprf.oprf.data` object are supplied).

    >>> k = key()
    >>> m = mask(k)

    The two objects ``k`` and ``m`` can now be used to mask data.

    >>> d = oprf.data.hash('abc')
    >>> mask(k, m, d) == oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)
    True

    If a :obj:`~oprf.oprf.mask` object is supplied, a :obj:`~oprf.oprf.data`
    object must also be supplied.

    >>> mask(k, m)
    Traceback (most recent call last):
      ...
    ValueError: data to be masked must be supplied
    """
    # If no mask is supplied, return a new encrypted mask.
    if m is None:
        return oprf.mask(bcl.symmetric.encrypt(k, oprf.mask()))

    if d is None:
        raise ValueError('data to be masked must be supplied')

    # Return the masked data.
    return oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)

def handler(k: bcl.secret, request: Union[str, dict]) -> dict:
    """
    Wrapper for service function that accepts inputs as a JSON
    string or a Python :obj:`dict` instance (*e.g.*, for use within a route
    defined using the `Flask <https://flask.palletsprojects.com>`__
    library).

    It is possible to request a new encrypted mask. Note that an empty request
    *must* be supplied to the handler.

    >>> k = key()
    >>> r = handler(k, {})
    >>> r['status']
    'success'
    >>> r = handler(k, '{}')
    >>> r['status']
    'success'

    The encrypted mask can be used to mask data. Note that it is the
    responsibility of the service implementation to maintain and supply
    the :obj:`~bcl.bcl.secret` key to the handler.

    >>> m = oprf.mask.from_base64(r['mask'][0])
    >>> d = oprf.data.hash('abc')
    >>> r = handler(k, {'mask': [m.to_base64()], 'data': [d.to_base64()]})
    >>> r['status']
    'success'

    The example below reproduces the example above, but submits the request
    to the handler as a string.

    >>> (m_str, d_str) = (str(m.to_base64()), str(d.to_base64()))
    >>> s = '{"mask": ["' + m_str + '"], "data": ["' + d_str + '"]}'
    >>> r = handler(k, s)
    >>> r['status']
    'success'

    The example below confirms that the response contains the masked data.

    >>> oprf.data.from_base64(r['data'][0]) == (
    ...     oprf.mask(bcl.symmetric.decrypt(k, bcl.cipher(m)))(d)
    ... )
    True

    If the supplied request is not valid (*e.g.*, if the data is missing),
    then the returned response indicates failure.

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
