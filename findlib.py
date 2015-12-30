from lxml import html
import requests

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
        initialpage = requests.get( initialrequest )
        if initialpage.status_code != 200:
            return '<ERROR>HTTP request returns code :{}'.format(initialpage.status_code)
        initialtree = html.fromstring(initialpage.content)
        if '<h2>No products found.<h2>' in initialpage.content:
            return '<WARNING>Barcode {} not found on www.yoopsie.com in {}'.\
                format(self.barcode, self.category)
        self.url = initialtree.xpath('//a[@target="_blank"]/attribute::href')[0]
        targetpage = requests.get( self.url )
        self.tree = html.fromstring(targetpage.content)
        self.keywords = self.tree.xpath('//meta[@name="keywords"]/attribute::content')
        titles = self.tree.xpath('//title/text()')
        parts = [s.lstrip() for s in titles[0].split(':')]
        self.name = parts[0]
        return '<OK>{}'.format(titles[0])

