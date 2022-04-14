=====
oprfs
=====

Easy-to-deploy oblivious pseudo-random function (OPRF) service that allows other parties (typically participants in some secure multi-party computation protocol) to obtain a persistent mask which they cannot decrypt but which they can safely apply (via requests to the service) to private data values of their choice.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/oprfs.svg
   :target: https://badge.fury.io/py/oprfs
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/oprfs/badge/?version=latest
   :target: https://oprfs.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/nthparty/oprfs/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/nthparty/oprfs/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/nthparty/oprfs/badge.svg?branch=main
   :target: https://coveralls.io/github/nthparty/oprfs?branch=main

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

Deployment Example: HTTP Server and Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is in illustration of how an instance of the OPRF service might be deployed using `Flask <https://flask.palletsprojects.com/>`_::

    import oprfs
    import flask
    app = flask.Flask(__name__)

    # Normally, a persistent key should be retrieved from secure storage.
    # Here, a new key is created each time so older masks cannot be reused
    # once the service is restarted.
    key = oprfs.key()

    @app.route('/', methods=['POST'])
    def endpoint():
        # Call the handler with the key and request, then return the response.
        return flask.jsonify(oprfs.handler(key, flask.request.get_json()))

    app.run()

Once an instance of the above service is running, a client might interact with it as illustrated in the example below. Note the use of the distinct `oprf <https://pypi.org/project/oprf/>`_ library to represent a data instance (which is itself a wrapper for an `Ed25519 <https://ed25519.cr.yp.to/>`_ group element as represented by an instance of the ``point`` class in the `oblivious <https://pypi.org/project/oblivious/>`_ library)::

    import json
    import requests
    import oprf

    # Request an encrypted mask.
    response = requests.post('http://localhost:5000', json={})
    mask_encrypted = json.loads(response.text)['mask'][0]

    # Mask some data.
    data = oprf.data.hash('abc').to_base64()
    response = requests.post(
        'http://localhost:5000',
        json={'mask': [mask_encrypted], 'data': [data]}
    )
    data_masked = oprf.data.from_base64(json.loads(response.text)['data'][0])

Documentation
-------------
.. include:: toc.rst

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org/>`_::

    cd docs
    python -m pip install -r requirements.txt
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. ../setup.py && make html

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org/>`_ (see ``setup.cfg`` for configuration details)::

    python -m pip install pytest pytest-cov
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python oprfs/oprfs.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    python -m pip install pylint
    python -m pylint oprfs

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.

Publishing
----------
This library can be published as a `package on PyPI <https://pypi.org/project/oprfs/>`_ by a package maintainer. Install the `wheel <https://pypi.org/project/wheel/>`_ package, remove any old build/distribution files, and package the source into a distribution archive::

    python -m pip install wheel
    rm -rf dist *.egg-info
    python setup.py sdist bdist_wheel

Next, install the `twine <https://pypi.org/project/twine/>`_ package and upload the package distribution archive to PyPI::

    python -m pip install twine
    python -m twine upload dist/*
