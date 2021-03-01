=====
oprfs
=====

Easy-to-deploy oblivious pseudo-random function (OPRF) service that allows other parties (typically participants in some secure multi-party computation protocol) to obtain a persistent mask which they cannot decrypt but which they can safely apply (via requests to the service) to private data values of their choice.

|pypi| |travis|

.. |pypi| image:: https://badge.fury.io/py/oprfs.svg
   :target: https://badge.fury.io/py/oprfs
   :alt: PyPI version and link.

.. |travis| image:: https://travis-ci.com/nthparty/oprfs.svg?branch=main
   :target: https://travis-ci.com/nthparty/oprfs

Purpose
-------
This library makes it possible to deploy a service that allows other parties to request an encrypted mask (which they cannot decrypt themselves but the service can decrypt) for an `oblivious pseudo-random function (OPRF) <https://en.wikipedia.org/wiki/Pseudorandom_function_family>`_ protocol. Those other parties can then ask the service to apply the mask to their own private, encrypted data values (which the service cannot decrypt). Thanks to the underlying `oblivious <https://pypi.org/project/oblivious/>`_ library, users of this library have the option of relying either on pure Python implementations of cryptographic primitives or on wrappers for `libsodium <https://github.com/jedisct1/libsodium>`_.

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install oprfs

The library can be imported in the usual ways::

    import oprfs
    from oprfs import *

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `nose <https://nose.readthedocs.io/>`_ (see ``setup.cfg`` for configution details)::

    nosetests

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python oprfs/oprfs.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint oprfs

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
