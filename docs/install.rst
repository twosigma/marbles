Installation
============

marbles can be installed from `PyPi`_.

.. _PyPi: https://pypi.org/project/marbles

.. note::

   We don't care what tool you use (we'll leave that to the `Python Packaging Guide`_), but we do highly recommend that you only install marbles into a virtual environment.

   .. _Python Packaging Guide: https://packaging.python.org/guides/tool-recommendations/#application-dependency-management

marbles contains two namespace packages: :mod:`marbles.core` and :mod:`marbles.mixins`. You can install them together or separately. For example, if you don't need any of the custom assertions in :mod:`marbles.mixins`, you can install and depend on :mod:`marbles.core` by itself.

pip
---

To install marbles with pip

.. code-block:: bash

   pip install marbles
   # -or-
   pip install marbles.core
   pip install marbles.mixins

.. _install-source:

Source
------

If you need a copy of the source, you can clone the `GitHub`_ repository or download the `tarball`_.

GitHub
^^^^^^

.. code-block:: bash

   git clone https://github.com/twosigma/marbles.git
   cd marbles
   pip install .

Tarball
^^^^^^^

.. code-block:: bash

   curl -OL https://github.com/twosigma/marbles/tarball/master
   tar xvzf /path/to/archive.tar.gz
   cd marbles
   pip install .
