from findlib import MediaObject, HtmlMenu, createdbsession, appconfig, BaseObject, LocationObject
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from models import Locations, Media
from forms import BasicForm, MediaForm, LocationsForm
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func


app = Flask(__name__)
app.config.from_pyfile('flaskcfg.cfg')
app.config.from_envvar('APP_SETTINGS', silent=True)


# Read configuration
config = appconfig('mediadb.cfg')

# Connect to database
session = createdbsession(config.get('Database', 'Name'),
                          sqlecho=False,
                          cleardown=False)


def chooseobject(option=None, *args):
    if option == 'media':
        obj = MediaObject(session, args[0])
    elif option == 'location':
        obj = LocationObject(session, Locations)
    else:
        obj = None
    return obj


def createstaticquery(querymodel):
    queryobj = session.query(querymodel). \
        order_by(querymodel.title)
    return queryobj


def initstaticform(formtemplate=BasicForm):
    return formtemplate()


def populatelist(option, *args):
    form = []
    option, querytable, pagetitle = setquerytable(option)
    if option is None:
        form.append(initstaticform())
    if args[0] is not None:
        pagetitle = pagetitle + '-' + args[0]
    queryobj = createstaticquery(querytable)
    deleteoption = []
    addfeatureoption = []
    addcategoryoption = []
    updateoption = []
    optionobject = chooseobject(option, args[0])
    for data_row in queryobj:
        form.append(optionobject.loadform(data_row, True))
        form[-1].media.data = optionobject.checkusage(data_row.locationid)
        if form[-1].media.data == []:
            deleteoption.append('<a href="/delete/{}/{}">Del</a>'.format(option, data_row.locationid))
        else:
            deleteoption.append('')

    return option, pagetitle, form, deleteoption, addfeatureoption, addcategoryoption, updateoption


def setform(option, req=None, modify=False):
    if option == 'media':
        form = MediaForm(req)
    elif option == 'location':
        form = LocationsForm(req)
    else:
        form = BasicForm()
    if modify:
        del form.media
    return form


def setquerytable(option):
    if option == 'media':
        querytable = Media
        pagetitle = 'Media'
    elif option == 'location':
        querytable = Locations
        pagetitle = 'Locations'
    else:
        querytable = Locations
        pagetitle = 'Invalid Option'
        option = None
    return option, querytable, pagetitle


def checknew(option, *argv):
    arglst = []
    for arg in argv:
        arglst.append(arg)
    name = arglst[0]
    option, querytable, notused = setquerytable(option)
    qry = session.query(querytable).filter(querytable.name == name)
    if option == 'location':
        sublocation = arglst[1]
        qry = qry.filter(querytable.sublocation == sublocation)
    elif option == 'media':
        locationid = arglst[1]
        qry = qry.filter(querytable.locationid == locationid)
    try:
        qry.one()
        return False
    except NoResultFound:
        return True


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


def getnewstaticid(table):
    qry = session.query(func.max(table.locationid))
    return getnextid(session, qry)


def adddata(option, form):
    add_item = None
    if option == 'media':
        # Use the NewComponent object to add this
#        fileobj = FileLoad('PASS', session)
        formdata = []
        loc = LocationObject(session, Locations)
        locdata = loc.getdatabyid(form.location.data)
        for field in form:
            if field.label.text == 'Location':
 #               fileobj.titles.append('Sublocation')
                formdata.append(locdata.Sublocation)
 #               fileobj.titles.append(field.label.text)
                formdata.append(locdata.Name)
            else:
#                fileobj.titles.append(field.label.text)
                formdata.append(field.data)
#        component = NewComponent(fileobj, formdata)
#        status = component.parsedata()
#        print status

    elif option == 'location':
        staticid = getnewstaticid(Locations)
        add_item = Locations(locationid=staticid, name=form.title.data, description=form.description.data,
                             sublocation=form.sublocation.data)
    else:
        querytable = Locations
    if add_item is not None:
        session.add(add_item)
        session.commit()
        flash('Added {} {}'.format(option, form.title.data))


@app.route('/')
def index():
    menu = HtmlMenu('Media Catalogue')
    menu.url.append('/showlist/books')
    menu.label.append('List Books')
    menu.url.append('/showlist/cds')
    menu.label.append('List CDs')
    menu.url.append('/showlist/dvds')
    menu.label.append('List DVDs')
    menu.url.append('/datamaint')
    menu.label.append('Data Maintenance')
    return render_template('menu.html', menu=menu, numrows=len(menu.url))


# Static Data Maintenance menu
@app.route('/datamaint')
def datamaintmenu():
    menu = HtmlMenu('Media Data Maintenance Menu')
    menu.label.append('Add/Update Locations')
    menu.url.append('/maintstaticdata/location')
    menu.label.append('Add Media by Title')
    menu.url.append('/maintstaticdata/mediabytitle')
    menu.label.append('Add Media by Barcode')
    menu.url.append('/maintstaticdata/mediabybarcode')
    menu.label.append('Add Media from Barcode File')
    menu.url.append('/maintstaticdata/mediafromfile')
    menu.label.append('List Unrecognised Barcodes')
    menu.url.append('/listbarcodes')
    return render_template('menu.html', menu=menu, numrows=len(menu.url))


@app.route("/maintstaticdata/<option>/<mediatype>", methods=['GET', 'POST'])
def maintstaticdata(option='media', mediatype=None):
    (option, pagetitle, form, deleteoptions, addfeatureoptions, categoriesopt, updateoption) = \
        populatelist(option, mediatype)
    return render_template('maintstatic.html', statictitle=pagetitle, form=form,
                           numrows=len(form), option=option, deleteoption=deleteoptions,
                           featureoption=addfeatureoptions, categoryoption=categoriesopt, updateoption=updateoption)


@app.route('/add/<option>', methods=['GET', 'POST'])
def addelement(option=None):
    form = setform(option, request.form, modify=True)
    if request.method == 'POST':
        if option == 'location':
            if checknew(option, form.title.data, form.sublocation.data):
                adddata(option, form)
        elif option == 'media':
            if checknew(option, form.title.data, form.location.data):
                adddata(option, form)

        (option, pagetitle, form, deleteoptions, addfeatureoptions, categoriesopt, updateoption) = populatelist(option)
        return render_template('maintstatic.html', statictitle=pagetitle, form=form,
                               numrows=len(form), option=option, deleteoption=deleteoptions,
                               featureoption=addfeatureoptions, categoryoption=categoriesopt,
                               updateoption=updateoption)
    else:
        form = setform(option, None, modify=True)
        if option == 'media':
            # Add location choices
            form.location.choices = \
                [(a.locationid, a.name+'::'+a.sublocation) for a in session.query(Locations).order_by('name')]

    return render_template('addelement.html', form=form, statictitle=option)


@app.route('/delete/<option>/<elementid>', methods=['GET', 'POST'])
def deleteelement(option=None, elementid=None):
    obj = chooseobject(option)
    if request.method == 'POST':
        # confirm button was pressed and delete
        flash(obj.delete(elementid))
        # refresh the list
        (option, pagetitle, form, deleteoptions, addfeatureoptions, categoriesopt, updateoption) = populatelist(option)
        return render_template('maintstatic.html', statictitle=pagetitle, form=form,
                               numrows=len(form), option=option, deleteoption=deleteoptions,
                               featureoption=addfeatureoptions, categoryoption=categoriesopt,
                               updateoption=updateoption)
    else:
        form = obj.loadform(obj.getdatabyid(elementid), False)
    return render_template('delelement.html', form=form, statictitle=option, readlock='True', elementid=elementid)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
