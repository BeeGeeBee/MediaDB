from findlib import MediaObject, HtmlMenu
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
