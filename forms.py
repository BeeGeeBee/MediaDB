from wtforms import Form, StringField, IntegerField, widgets,\
    SelectField, DecimalField, HiddenField, BooleanField, RadioField
from wtforms.validators import Length


class BasicForm(Form):
    description = StringField('Description', [Length(max=250)])
    title = StringField('Title', [Length(min=1, max=250)])
    media = StringField('Used By', [Length(max=1000)])


class MediaForm(BasicForm):
    id = HiddenField('', [Length(max=3)])
    mediatype = SelectField('Type', [Length(max=50)])
    location = SelectField('Location', [Length(max=100)])
    url = StringField('URL', [Length(max=250)])
    barcode = StringField('Barcode', [Length(max=20)])


class LocationsForm(BasicForm):
    sublocation = StringField('Sublocation', [Length(max=50)])
