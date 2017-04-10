=================
Assertion Logging
=================

You can configure :mod:`marbles` to record structured log information
about every assertion made during a test run as a json blob.

This can capture the type of assertion made, any
:class:`~unittest.TestCase` attributes you've configured (often,
metadata about the resource being tested), the result of the
assertion, and any ``locals`` captured at assertion time.

These logs can be transferred to another system for later analysis,
reporting, etc. For example, you could run :program:`logstash` after a
test run to put these logs into Elasticsearch, and use Kibana later on
to analyze them, maybe creating dashboards that show how many
assertion failures you get over time, grouped by resource type or by
some other value, like a :data:`severity` attribute within your test.

Setup
-----

Use :meth:`marbles.log.AssertionLogger.configure` to instruct marbles
where it should write the logfile. There you can also instruct it
about which :class:`~unittest.TestCase` attributes it should log.

You can do this in your test suite's ``__main__`` module::

   from marbles.log import logger

   if __name__ == '__main__':
       logger.configure(logfile='/path/to/marbles.log',
                        attrs=['filename', 'category'])
       unittest.main()

You can also override the logging configuration using environment
variables. For example, if you need to see verbose logs, you can
re-run with ``MARBLES_LOG_VERBOSE=true``.

For more details about configuring, see the documentation for
:mod:`marbles.log`.
