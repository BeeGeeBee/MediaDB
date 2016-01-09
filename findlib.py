from lxml import html
import requests
import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from models import Base


def appconfig(configfile):
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    return config


def createdbsession(dbname=None, sqlecho=None, cleardown=False):
    engine = create_engine(dbname, echo=sqlecho, poolclass=NullPool)
    Base.metadata.bind = engine

    dbsession = sessionmaker()
    dbsession.bind = engine
    session = dbsession()
    # Add the schema
    # If cleardown then drop all first
    if cleardown:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return session


class MediaObject(object):
    def __init__(self, category=None):
        self.barcode = None
        self.name = ''
        self.url = ''
        self.category = category
        self.keywords = ''
        self.tree = ''

    def getbybarcode(self):
        if not self.barcode:
            return '<ERROR> No barcode defined.'
        if not self.category:
            return '<ERROR> No category defined.'
        initialrequest = \
            'http://www.yoopsie.com/query.php?query={}&locale=UK&index={}'.\
            format(self.barcode, self.category)
        initialpage = requests.get(initialrequest)
        if initialpage.status_code != 200:
            return '<ERROR>HTTP request returns code :{}'.format(initialpage.status_code)
        initialtree = html.fromstring(initialpage.content)
        if '<h2>No products found.<h2>' in initialpage.content:
            return '<WARNING>Barcode {} not found on www.yoopsie.com in {}'.\
                format(self.barcode, self.category)
        self.url = initialtree.xpath('//a[@target="_blank"]/attribute::href')[0]
        targetpage = requests.get(self.url)
        self.tree = html.fromstring(targetpage.content)
        self.keywords = self.tree.xpath('//meta[@name="keywords"]/attribute::content')
        titles = self.tree.xpath('//title/text()')
        parts = [s.lstrip() for s in titles[0].split(':')]
        self.name = parts[0]
        return '<OK>{}'.format(titles[0])


class HtmlMenu(object):
    def __init__(self, title):
        self.title = title
        self.url = []
        self.label = []
