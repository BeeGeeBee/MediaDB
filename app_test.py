import os
#import app
import unittest
import tempfile
import StringIO
from findlib import MediaObject

__author__ = 'bernie'


class ComponentsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_02_books(self):
        mediatest = MediaObject()
        mediatest.barcode = '9780007304462'
        response = mediatest.getbybarcode()
        assert '<ERROR> No category defined.' in response
        mediatest = MediaObject(category='Books')
        response = mediatest.getbybarcode()
        assert '<ERROR> No barcode defined.' in response
        mediatest.barcode = '9780007304462'
        response = mediatest.getbybarcode()
        print response
        assert '<OK>Azincourt:' in response
