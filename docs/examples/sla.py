import re
import unittest
from datetime import date, datetime, timedelta

from marbles.core import marbles


filename = 'data.csv'
# Fake data that, in the real world, we would read in from data.csv
data = '12345,2017-01-01,iPhone 7,649.00,123-45-6789'


class SLATestCase(marbles.TestCase):
    '''SLATestCase makes sure that SLAs are being met.'''

    # Class attributes are helpful for storing information that
    # is needed in more than one advice annotation and that won't
    # change between tests
    data_engineer = 'Jane Doe'
    lc_contact = 'lc@company.com'
    vendor_id = 'V100'

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
        advice = '''This test will fail if

    1) the vendor provided data containing SSNs, and

    2) our internal SSN filtering is unsuccessful.

The vendor should not provide data containing PII, and this incident
should be reported to Legal & Compliance ({self.lc_contact})
immediately. In your report, please include the vendor ID,
{self.vendor_id}, and the name of the file containing the PII,
{self.filename}.

Our internal PII filtering algorithm is maintained here: {_ssn_filter}.
Create a new issue on that project to report this bug and assign it to
{self.data_engineer}, but *do not* include any PII in the issue.
'''

        _ssn_filter = 'http://gitlab.com/group/repo'  # noqa: F841
        ssn_regex = '\d{3}-?\d{2}-?\d{4}'

        self.assertNotRegex(self.data, ssn_regex, advice=advice)


if __name__ == '__main__':
    unittest.main()
