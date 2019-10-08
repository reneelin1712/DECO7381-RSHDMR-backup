import os
import flask
import pymysql
from flask import render_template
from flask import request, redirect, url_for
from hdmr2 import rshdmr
from werkzeug.utils import secure_filename
import json  # transform the strings to json
from flask import send_file  # allow the server to send files
from flask_cors import CORS, cross_origin  # solving cross origin errors
from pymongo import MongoClient  # connecting mongoDB with flask
from flask import session

s = "pdfname"
# our database is running on default port 27017
client = MongoClient('mongodb://localhost:27017/')
db = client.rshdmr  # select the database created for this project
collection = db.users  # our user info is save in the users collection

app = flask.Flask("__name__")
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/upload": {"origins": "http://www.rshdmr.com"}})

# the home route, it returns our single webpage
@app.route('/')
def home():
    return flask.render_template('index.html', token="helloflask")


@app.route('/calculate')
def hdmr_test():
    test = 'average_sediment.csv'
    result = rshdmr(test)
    result.auto()
    result.stats()
    return flask.render_template('index.html')


# csv file send through this route
@app.route('/upload', methods=['POST'])
@cross_origin(origin='http://www.rshdmr.com', headers=['Content- Type', 'Authorization'])
def upload_file():
    file = request.files['file']
    if request.method == 'POST':
        if file.filename == '':
            flask('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            print(file)
            file.save(filename)
            tempResult = [{'factor': 'test feedback sensitive factor1'}, {
                'factor': 'test feedback sensitive factor2'}]
            # result = rshdmr(filename)
            # result.auto()
            # result.stats()
            result = rshdmr(filename)
            result.auto()
            test = result.stats()

            # result.create_pdf(os.path.join('pdf/', filename))
            pdfname = file.filename.split('.')[0]
            global s
            s = pdfname + '.pdf'
            print(session.get('pdfname'))
            result.create_pdf(pdfname)
            return json.dumps(test)
            # return json.dumps(tempResult)

    # return redirect(url_for('fileFrontPage'))

# return the image generated by RSHDMR algorithm
@app.route('/image.png')
def get_image():
    filename = 'foo.png'
    return send_file(filename, mimetype='image/png')

# new user signup
@app.route('/signup', methods=['POST'])
@cross_origin(origin='http://www.rshdmr.com', headers=['Content- Type', 'Authorization'])
def signup():
    newUser = request.json  # parse the post request to a json object
    if not request.json:
        return "not a json post"
    collection.insert_one(newUser)  # insert the new object to mongoDB
    return {"message": "json post succeeded"}


@app.route('/download-pdf')
def return_files_tut():
    try:
        return send_file(s, attachment_filename='report.pdf', as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/login', methods=['POST'])
@cross_origin(origin='http://www.rshdmr.com', headers=['Content- Type', 'Authorization'])
def login():
    print(request.json)
    currentUser = request.json.get('email')
    if not request.json:
        return "not a json post"
    query = collection.find_one({"email": currentUser})

    print(query.get('name'))
    return query.get('name')

# uploadwithsetting
@app.route('/uploadwithsetting/<poly>/<param1>', methods=['POST', 'GET'])
@cross_origin(origin='http://www.rshdmr.com', headers=['Content- Type', 'Authorization'])
def upload_file_withsetting(poly, param1):
    file = request.files['file']
    poly = int(poly)
    if request.method == 'POST':
        if file.filename == '':
            flask('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            print(file)
            file.save(filename)

            result = rshdmr(filename, poly, param1)
            result.auto()
            test = result.stats()

            pdfname = file.filename.split('.')[0]
            global s
            s = pdfname + '.pdf'
            print(session.get('pdfname'))
            result.create_pdf(pdfname)
            return json.dumps(test)


if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=80,debug=True)
    app.run(host='0.0.0.0', port=8000, debug=True)