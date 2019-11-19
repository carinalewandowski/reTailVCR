#!/usr/bin/env python

#-----------------------------------------------------------------------
# backend server
# Author: Paskalino Spirollari
#-----------------------------------------------------------------------

from sys import argv, stderr, exit
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, session
from database_interaction import Database
from CASClient import CASClient
import random
#import psycopg2

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

# Generated by os.urandom(16)                                                                                                                      
app.secret_key = b'\rb\x98G`\xaa\xb5\xa6i$\xe0TWk\x0b\x1e'

#-----------------------------------------------------------------------

def check_user(netid):
    database = Database()
    database.connect()
    
    if not database.user_exists(netid):
        database.add_user(netid)

    database.disconnect()

#-----------------------------------------------------------------------

@app.route('/item', methods=('GET', 'POST'))
def item():
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')

    itemid = request.args.get('itemid')

    if request.method == 'POST':
        bid = request.form['bid']
        print(bid)
        if bid is None:
            bid = ''
        #if netid is None:
        netid = 'carinal'

        # add listing to database
        database = Database()
        database.connect()
        database.bid(itemid, bid, netid)
        entry = database.get_item(itemid)
        database.disconnect()

        html = render_template('item.html', entry=entry[0])
        response = make_response(html)
        return response
    else:
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

@app.route('/sell', methods=('GET', 'POST'))
def sell():
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')

    # parse user input for item upload details
    # ***** need to handle other info still *****
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        if title is None:
            title = ''
        if description is None:
            description = ''
        if price is None:
            price = ''
        #if itemid is None:
        itemid = random.uniform(100, 1000000)
        #if postdate is None:
        postdate = '2019-11-18'
        #if netid is None:
        netid = 'carinal'
        #if image is None:
        image = ''
    
        # add listing to database
        database = Database()
        database.connect()
        database.add_to_db(itemid, postdate, netid, price, image, description, title)
        database.disconnect()

        html = render_template('confirmation.html')
        response = make_response(html)
        return response

    else:
        try:
            html = render_template('sell.html')
            response = make_response(html)
            return response
        except Exception as e:
            print("error" + str(e), file=stderr)
            exit(1)

#-----------------------------------------------------------------------

@app.route('/track', methods=('GET', 'POST'))
def track():
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')

    if request.method == 'POST':
        print("requesting")
        itemid = request.form['itemid']
        print(itemid)

        database = Database()
        database.connect()
        database.delete_from_db(itemid)

        netid_results = database.get_all_items_from_netid('carinal')
        bidder_results = database.get_all_items_from_maxbidder('carinal')

        database.disconnect()

        html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
        response = make_response(html)
        return response

    else:
        database = Database()
        database.connect()
        netid_results = database.get_all_items_from_netid("carinal")
        bidder_results = database.get_all_items_from_maxbidder("carinal")
        database.disconnect()

        html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
        response = make_response(html)
        return response

#-----------------------------------------------------------------------

@app.route('/redirect_home_control')
@app.route('/index')
@app.route('/')
def home_control():
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')

    try:
        database = Database()
        database.connect()
        results = database.get_available_db()
        database.disconnect()

        html = render_template('index.html', results=results, lastSearch='')
        response = make_response(html)
        response.set_cookie('lastSearch', '')
        return response

    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1) 
    
#-----------------------------------------------------------------------

@app.route('/history_control')
def history_control():
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')

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
    if 'username' not in session:
        username = CASClient().authenticate()
        check_user(username)
    else:
        username = session.get('username')
        
    try:
        string = request.args.get('string')
        if (string is None) or (string.strip() == ''):
            string = ''
        
        database = Database()
        database.connect()
        results = database.search(string)
        database.disconnect()

        html = render_template('index.html', results=results, lastSearch=string)
        response = make_response(html)
        response.set_cookie('lastSearch', string)
        return response
        
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
