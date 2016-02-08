import unittest
from findlib import MediaObject, appconfig, createdbsession
import os
import app
import csv
from models import Locations, Media

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

# Set up the database for the rest of the tests
    def test_02_00(self):
        dbsession = createdbsession('sqlite:///testdatabase.db', sqlecho=False, cleardown=True)
        with open('testlocations.csv', mode='r') as fp:
            csvreader = csv.reader(fp)
            for data in csvreader:
                add_location = Locations(locationid = data[0], name = data[1], description = data[2],
                                         sublocation = data[3])
                dbsession.add(add_location)
                print data
        with open('testmedia.csv', mode='r') as fp:
            csvreader = csv.reader(fp)
            for data in csvreader:
                add_media = Media(mediaid = data[0],
                                  mediatype = data[1],
                                  title = data[2],
                                  description = data[3],
                                  url = data[4],
                                  barcode = data[5],
                                  locationid = data[6])
                dbsession.add(add_media)
                print data
        dbsession.commit()

# Check Options to
# list books, CDS, DVDs
# data maintenance
    def test_02_checkopions(self):
        rv = self.app.get('/')
        assert 'List Books' in rv.data
        assert 'List CDs' in rv.data
        assert 'List DVDs' in rv.data
        assert 'Data Maintenance' in rv.data

# Static data maintenance options
# Add/Update Locations
# Add media by title
# Add media by barcode
# Load media from barcode file
# List unrecognised barcodes
    def test_02_datamaintoptions(self):
        rv = self.app.get('/datamaint')
        assert 'Add/Update Locations' in rv.data
        assert 'Add Media by Title' in rv.data
        assert 'Add Media by Barcode' in rv.data
        assert 'Add Media from Barcode File' in rv.data
        assert 'List Unrecognised Barcodes' in rv.data

# Maintain Locations
    def test_02_locations(self):
        rv = self.app.get('/maintstaticdata/location')
        # Page labelled correctly
        assert 'Maintain Locations' in rv.data
        # Page contains a delete option column.
        assert 'Delete' in rv.data
        # Should not offer delete for established location
        assert '"/delete/location/1"' not in rv.data
        # Table should have a Used By header
        assert 'Used By' in rv.data
        # Should see DVD referenced
        assert "'Test DVD Media'" in rv.data
        # Page displays current locations
        assert 'Lounge' in rv.data
        # Page gives the option to add a location
        assert '"addButton"' in rv.data
        # Add a location
        rv = self.app.post('/add/location', data=dict(
            title='Test location',
            description='This is a test location',
            sublocation='A test sublocation'
        ))
        assert 'Test location' in rv.data
        assert 'This is a test location' in rv.data
        assert 'A test sublocation' in rv.data
        # Check delete option available
        assert '"/delete/location/2"' in rv.data
        # Delete this new location
        rv = self.app.post('/delete/location/2')
        assert 'Successfully deleted ID 2 Test location' in rv.data
        # Cannot delete a location in use
        rv = self.app.post('/delete/location/1')
        assert 'Cannot delete Lounge. It is referenced by media(s)' in rv.data

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

# Maintain media
    def test_02_maintmedia(self):
        rv = self.app.get('/maintstaticdata/media/Books')
        print rv.data
        # Page labelled correctly
        assert 'Maintain Media-Books' in rv.data
        # Page displays current books
        assert 'Test Book Media' in rv.data
        # Page contains a delete option column.
        assert 'Delete' in rv.data
        # Page contains an update option column.
        assert 'Updt' in rv.data
        # Page gives the option to add a book
        assert '"addButton"' in rv.data
        # Table should not have a Used By header
        assert 'Used By' not in rv.data
        # Add a book
        rv = self.app.post('/add/component', data=dict(
            title='Test book',
            description='This is a test book',
            mediatype='3',
            location='1'
        ))
        assert 'Test book' in rv.data
        assert 'This is a test book' in rv.data
        # Check delete option available
        assert '"/delete/component/4"' in rv.data
        # Update the book.
        rv = self.app.post('/update/media/4', data=dict(
                title='Updated Test'
            ))
        assert 'Updated media Updated Test' in rv.data
        # Delete this new media
        rv = self.app.post('/delete/media/4')
        assert 'Successfully deleted ID 4 Updated Test' in rv.data

