import requests
import marbles.core


# We stub out a put request for the purposes of creating an example
# test that will always fail, but that is more interesting than the
# usual examples like assertTrue(False)
class Response(object):

    def __init__(self, status_code, reason):
        self._status_code = status_code
        self._reason = reason

    @property
    def status_code(self):
        return self._status_code

    @property
    def reason(self):
        return self._reason


class requests(object):  # noqa: F811

    @classmethod
    def put(cls, endpoint, data=None):
        return Response(status_code=409,
                        reason=('The request could not be completed '
                                'due to a conflict with the current '
                                'state of the target resource.'))


class ResponseTestCase(marbles.core.TestCase):

    def test_create_resource(self):
        endpoint = 'http://example.com/api/v1/resource'
        data = {'id': 1, 'name': 'Little Bobby Tables'}

        res = requests.put(endpoint, data=data)
        self.assertEqual(
            res.status_code,
            201
        )


if __name__ == '__main__':
    marbles.core.main()
