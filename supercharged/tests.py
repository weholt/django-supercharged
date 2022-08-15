from django.test import TestCase

from supercharged.services import (
    ExpectedDifferentProductException,
    ExpectedNoProductException,
    ServiceCall,
    ServiceProcessResult,
)


class ServiceCallTest(TestCase):
    """
    Tests related to the ServiceCall decorator
    """

    def test_1(self):
        """!!"""

        @ServiceCall(int)
        def add(a, b):
            return ServiceProcessResult.produce(a + b)

        result = add(1, 1)
        self.assertEqual(result.product, 2)

    def test_2(self):
        """!!"""

        @ServiceCall()
        def add(a, b):
            return ServiceProcessResult.produce()

        self.assertRaises(ExpectedNoProductException, add, 1, 1)

    def test_3(self):
        """!!"""

        @ServiceCall("test")
        def add(a, b):
            return ServiceProcessResult.produce(a + b)

        self.assertRaises(ExpectedDifferentProductException, add, 1, 1)
