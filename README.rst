malva
=====

Malva, goes well with custard.

|travis|_ |coveralls|_


::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ twistd -n malva probe-modems
    2013-06-23 20:21:07+0200 [-] Log opened.
    2013-06-23 20:21:07+0200 [-] twistd 13.0.0 (/Users/sdehaan/Documents/Repositories/malva/ve/bin/python 2.7.2) starting up.
    2013-06-23 20:21:07+0200 [-] reactor class: twisted.internet.selectreactor.SelectReactor.
    2013-06-23 20:21:09+0200 [-] Port: /dev/tty.usbmodem1d112, IMSI: 655011570028658, Manufacturer info: K3772-Z
    2013-06-23 20:21:09+0200 [-] Port: /dev/tty.usbmodem1d114, IMSI: 655011570028658, Manufacturer info: K3772-Z
    2013-06-23 20:21:09+0200 [-] Main loop terminated.
    2013-06-23 20:21:09+0200 [-] Server Shut Down.


.. |travis| image:: https://travis-ci.org/smn/malva.png?branch=develop
.. _travis: https://travis-ci.org/smn/malva

.. |coveralls| image:: https://coveralls.io/repos/smn/malva/badge.png?branch=develop
.. _coveralls: https://coveralls.io/r/smn/malva

