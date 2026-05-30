import requests
import marbles.core


class CatalogTestCase(marbles.core.TestCase):

    def test_product_count(self):
        endpoint = 'https://example.com/api/v1/products'
        products = requests.get(endpoint).json()

        self.assertGreaterEqual(
            len(products),
            100,
            note=('The upstream catalog normally contains at least 100 '
                  'products. A lower count may indicate an incomplete '
                  'data refresh.')
        )
