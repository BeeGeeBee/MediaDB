import unittest
from findlib import MediaObject, appconfig, createdbsession
import os
import app

__author__ = 'bernie'


class MediaTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    # Define tests here. Unittest executes tests in alphabetical order of name.
    # Tests are defined as test_00_aaaaa - Config tests.
    # test_01_aaaaa - Database tests.
    # test_02_aaaaa - function tests.

    def test_00_config(self):
        config = appconfig('barcode_test.cfg')
        assert 'barcode_test.db' in config.get('Database', 'Name')

    def test_01_database(self):
        # Set up a session
        testsession = createdbsession('sqlite:///testdatabase.db', sqlecho=False, cleardown=True)
        testsession.close()
        os.unlink('testdatabase.db')

    # def test_99_end(self):
    #     os.unlink('testdatabase.db')

# Check Options to
# list books, CDS, DVDs
# data maintenance
    def test_02_checkopions(self):
        rv = self.app.get('/')
        assert 'List Books' in rv.data
        assert 'List CDs' in rv.data
        assert 'List DVDs' in rv.data
        assert 'Data Maintenance' in rv.data

    def test_02_books(self):
        """
        Test acquiring book data based on barcodes.
        :return:
        """
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
