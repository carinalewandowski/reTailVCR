#!/usr/bin/env python

#-----------------------------------------------------------------------
# backend server
# Author: Paskalino Spirollari
#-----------------------------------------------------------------------

from sys import argv, stderr, exit
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database_interaction import Database
#import psycopg2

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

@app.route('/item')
def item():
    itemid = request.args.get('itemid')

    try:
        database = Database()
        database.connect()
        entry = database.get_item(itemid)
        database.disconnect()
        html = render_template('item.html', entry=entry[0])
        response = make_response(html)
        return response
    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1)

#-----------------------------------------------------------------------

@app.route('/sell')
def sell():
    try:
        html = render_template('sell.html')
        response = make_response(html)
        return response
    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1)

#-----------------------------------------------------------------------

@app.route('/redirect_home_control')
@app.route('/index')
@app.route('/')
def home_control():
    try:
        print("1")

        database = Database()
        database.connect()
        results = database.get_available_db()
        database.disconnect()

        print(len(results))
        html = render_template('index.html', results=results)
        response = make_response(html)
        return response

    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1) 
    
#-----------------------------------------------------------------------

@app.route('/history_control')
def history_control():
    try:

        html = render_template('history_view.html')
        response = make_response(html)
        return response

    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1) 

#-----------------------------------------------------------------------

@app.route('/search')
def search():
    try:
        string = request.args.get('string')
        if (string is None) or (string.strip() == ''):
            string = ''
        
    except Exception as e:
        print('error' + str(e), file=stderr)
        exit(1)

#-----------------------------------------------------------------------


if __name__ == '__main__':
    # if len(argv) != 2:
    #     print('Usage: ' + argv[0] + ' port')
    #     exit(1)
    # # add things to db
    # # 
    # app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    app.run()
