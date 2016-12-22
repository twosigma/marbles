import re
import unittest
from datetime import date, datetime, timedelta

from marbles import AnnotatedTestCase


filename = 'data.csv'
# Fake data that, in the real world, we would read in from data.csv
data = '12345,2017-01-01,iPhone 7,649.00,123-45-6789'


class SLATestCase(AnnotatedTestCase):
    '''SLATestCase makes sure that SLAs are being met.'''

    def setUp(self):
        setattr(self, 'filename', filename)
        setattr(self, 'data', data)

    def tearDown(self):
        delattr(self, 'filename')
        delattr(self, 'data')

    def test_on_time_delivery(self):
        advice = '''The data in {self.filename} are out of date. If
this is a recurring issue, contact the data provider to negotiate
a reimbursement or to re-negotiate the terms of the contract.'''

        datadate = re.search('\d{4}-?\d{2}-?\d{2}', self.data).group(0)
        datadate = datetime.strptime(datadate, '%Y-%m-%d').date()
        on_time_delivery = date.today() - timedelta(1)

        self.assertGreaterEqual(datadate, on_time_delivery, advice=advice)

    def test_for_pii(self):
        advice = '''{self.filename} appears to contain SSN(s). Please
report this incident to legal and compliance.'''

        ssn_regex = '\d{3}-?\d{2}-?\d{4}'
        self.assertNotRegex(self.data, ssn_regex, advice=advice)


if __name__ == '__main__':
    unittest.main()
