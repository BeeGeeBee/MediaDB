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
        mediatest.barcode = '9780007304461'
        response = mediatest.getbybarcode()
        assert '<WARNING>Barcode 9780007304461 not found on www.yoopsie.com in Books' in response
        mediatest.barcode = '9780007304462'
        response = mediatest.getbybarcode()
        assert '<OK>Azincourt:' in response


    def test_02_dvds(self):
        mediatest = MediaObject()
        mediatest.barcode = '5030305514860'
        response = mediatest.getbybarcode()
        assert '<ERROR> No category defined.' in response
        mediatest = MediaObject(category='DVD')
        response = mediatest.getbybarcode()
        assert '<ERROR> No barcode defined.' in response
        mediatest.barcode = '5030305514861'
        response = mediatest.getbybarcode()
        assert '<WARNING>Barcode 5030305514861 not found on www.yoopsie.com in DVD' in response
        mediatest.barcode = '5030305514860'
        response = mediatest.getbybarcode()
        assert '<OK>Gnomeo & Juliet [DVD]:' in response
