from lxml import html
import requests
import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from models import Base, Media, Locations
from forms import LocationsForm

ERRNoFileName = 1
ERRFileNotFound = 2
ERRInvalidTitle = 3
ERRInvalidNumCols = 4
ERRSublocBeforeLoc = 5
ERRValueBeforeFeature = 6
ERRNoNameCol = 7


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


def getnextid(session, qry):
    """
    Get the next ID value.
    :param session: Database session object.
    :param qry: ORM query object to get the ID
    :return: Return an incremented ID or 1 if no IDs are defined.
    """
    nextid = qry.one()
    session.commit()
    data = nextid[0]
    if data is not None:
        return data + 1
    else:
        return 1


def getid(con):
    """

    :param con: Database ORM query object.
    :return: return the ID or 0.

    Given a name get the ID. If Name not found return 0

    """
    try:
        data = con.one()
        return data.ID
    except NoResultFound:
        return 0


def getusage(qry):
        result = None
        try:
            result = [str(comp[0]) for comp in qry.all()]
        except NoResultFound:
            pass
        return result


class BaseObject(object):
    def __init__(self, dbsession, table):
        self.ID = None
        self.Name = None
        self.Description = None
        self.dbsession = dbsession
        self.new = None
        self.table = table
        self.rowsparsed = 0
        self.rowsloaded = 0

    def setid(self):
        qry = self.dbsession.query(self.table).filter(self.table.Name == self.Name)
#        print self.Name, self.table
        self.ID = getid(qry)
        if self.ID == 0:
            qry = self.dbsession.query(func.max(self.table.ID))
            self.ID = getnextid(self.dbsession, qry)
            self.new = True
#            print '{} New ID is {}\n'.format(self.Name, self.ID)
        else:
            self.new = False

    def parsename(self, value):
        self.Name = value

    def parsedescription(self, value):
        self.Description = value

    def getdatabyname(self, name):
        qry = None
        if name is not None:
            try:
                qry = self.dbsession.query(self.table).filter(self.table.Name == name).one()
            except NoResultFound:
                qry = None
        return qry

    def getdatabyid(self, dataid):
        qry = None
        if dataid is not None:
            try:
                qry = self.dbsession.query(self.table).filter(self.table.locationid == dataid).one()
            except NoResultFound:
                qry = None
        return qry

    def checkusage(self, itemid):
        return []

    def delete(self, itemid):
        data = self.getdatabyid(itemid)
        if data:
            usage = self.checkusage(itemid)
            if usage != []:
                return 'Cannot delete {}. It is referenced by media(s) {}'.format(data.name, usage)
            else:
                name = data.name
                self.dbsession.query(self.table).filter(self.table.locationid == itemid).delete()
                self.dbsession.commit()
                return 'Successfully deleted ID {} {}'.format(itemid, name)
        return 'Cannot delete. ID {} does not exist.'.format(itemid)


class LocationObject(BaseObject):
    def __init__(self, dbsession, table):
        BaseObject.__init__(self, dbsession, table)
        self.Sublocation = None

    def getdatabyid(self, dataid):
        qry = None
        if dataid is not None:
            try:
                qry = self.dbsession.query(Locations).filter(Locations.locationid == dataid).one()
            except NoResultFound:
                qry = None
        return qry

    def checkusage(self, itemid):
        qry = self.dbsession.query(Media.title).filter(Media.locationid == itemid)
        return getusage(qry)

    def checkcomplete(self):
        if self.Name is not None and \
                self.Description is not None and \
                self.Sublocation is not None:
            if self.ID is None:
                self.setid()

    def parsesublocation(self, value):
        self.Sublocation = value
        self.checkcomplete()

    def add(self):
        if self.Description is None:
            self.Description = self.Name
        add_location = Locations(ID=self.ID, Name=self.Name, Description=self.Description,
                                 Sublocation=self.Sublocation)
        self.dbsession.add(add_location)
        self.dbsession.commit()
        return 'Adding location {} - {}, {}, {}\n'.format(self.ID, self.Name,
                                                          self.Description, self.Sublocation)

    def loadform(self, *argv):
        arglst = []
        for arg in argv:
            arglst.append(arg)
        componentdata = arglst[0]
        form = LocationsForm()
        form.title.data = componentdata.name
        form.description.data = componentdata.description
        form.sublocation.data = componentdata.sublocation
        return form

    def getdatabyname(self, name, sublocation=None):
        result = None
        if name is not None:
            qry = self.dbsession.query(self.table).filter(self.table.Name == name)
            if sublocation is not None:
                qry = qry.filter(self.table.Sublocation == sublocation)
            else:
                qry = qry.filter(self.table.Sublocation == '')
            try:
                result = qry.one()
            except NoResultFound:
                result = None
        return result
