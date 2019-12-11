#!/usr/bin/env python

#-----------------------------------------------------------------------
# backend server
# Author: Paskalino Spirollari
#-----------------------------------------------------------------------

from sys import argv, stderr, exit
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, session
from database_interaction import Database
from werkzeug.utils import secure_filename
from CASClient import CASClient
from PIL import Image
import io
import random
import string
import datetime
import os

from flask_mail import Mail
from flask_mail import Message
#import psycopg2

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'retail.cos333@gmail.com',
    "MAIL_PASSWORD": 'NZ_~m;9t'
}

app.config.update(mail_settings)
mail = Mail(app)




# Generated by os.urandom(16)                                                                                                                      
app.secret_key = b'\rb\x98G`\xaa\xb5\xa6i$\xe0TWk\x0b\x1e'
IMAGE_DIR_AVAILABLE = 'static/images/available'
IMAGE_DIR_PURCHASED = 'static/images/purchased'

database = Database()
database.connect()

stored_images = database.get_available_images()
purchased_images = database.get_purchased_images()

print("Retrieving available images...")
for entry in stored_images:
    image_data = entry[1]
    im = Image.open(io.BytesIO(image_data))
    imgpath = '{}/{}'.format(IMAGE_DIR_AVAILABLE, entry[2])
    im.save(imgpath)

print("Retrieving purchased images...")
for soldentry in purchased_images:
    image_data = soldentry[1]
    im = Image.open(io.BytesIO(image_data))
    imgpath = '{}/{}'.format(IMAGE_DIR_PURCHASED, soldentry[2])
    im.save(imgpath)

print("All Images Retrieved")
database.disconnect()

#-----------------------------------------------------------------------

def send_mail(buyer, seller, item, price):
    try: 
        # buyer_netid = buyer.strip()
        # print(buyer_netid)

        # seller_netid = seller.strip()
        # print(seller_netid)

        # # send to seller
        # sendee = seller_netid + "@princeton.edu"
        msg = Message(subject="reTail: Purchase Notification!", sender=app.config.get("MAIL_USERNAME"), 
            recipients=[seller], body='Your item, "{}", has been purchased for ${}. The buyer e-mail is {}. Please contact the buyer via e-mail to arrange a payment method and pick-up/drop-off details.\n\nThanks for using reTail!'.format(item, price, buyer))

        mail.send(msg)

        # send to buyer
        # sendee = buyer_netid + "@princeton.edu"
        msg = Message(subject="reTail: Purchase Notification!", sender=app.config.get("MAIL_USERNAME"), 
            recipients=[buyer], body='You have purhcased the item, "{}", for ${}. The seller e-mail is {}. Please contact the seller via e-mail to arrange a payment method and pick-up/drop-off details.\n\nThanks for using reTail!'.format(item, price, seller))

        mail.send(msg)
    except Exception as e:
        print("send_mail error: " + str(e))
        # do some other stuff so the people are informed.
        return


#-----------------------------------------------------------------------

def check_user(netid):
    database = Database()
    database.connect()
    
    if not database.user_exists(netid):
        database.add_user(netid)

    database.disconnect()

#-----------------------------------------------------------------------

def randstr():
    '''Creates a random string of alphanumeric characters.'''
    return ''.join(random.choice(string.ascii_uppercase + string.digits) \
                for _ in range(30))

#-----------------------------------------------------------------------

@app.route('/item', methods=('GET', 'POST'))
def item():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'
    itemid = request.args.get('itemid')

    string = request.cookies.get('lastSearch')
    if string is None:
        string = ''
    
    database = Database()
    database.connect()

    # check if item still exists in available database
    # if not, check if it was sold
    if not(database.check_exists_item(itemid)):
        if not(database.check_exists_solditem(itemid)):
            errormsg = 'Sorry, this item does not exist.'
            html = render_template('error.html', errormsg=errormsg)
            response = make_response(html)
            return response
        else:   
            entry = database.get_solditem(itemid)
            database.disconnect()
            errormsg = 'Sorry, this item has already been sold.'
            html = render_template('itemsold.html', entry=entry[0], errormsg=errormsg)
            response = make_response(html)
            return response

    if request.method == 'POST':
        bid = request.form['bid']

        # check if bid is numeric
        try:
            bid = float(bid)
        except Exception as e:
            database = Database()
            database.connect()
            entry = database.get_item(itemid)
            database.disconnect()
            msg = 'Please enter a valid bid.'
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string)
            response = make_response(html)
            return response

        # round bid to nearest 0.5
        bid = round( (float(bid) * 2) / 2 )

        #if netid is None:
        netid = username
        
        database = Database()
        database.connect()

        # add bid to database
        entry = database.get_item(itemid)
        seller_id = (entry[0])[2]
        print(seller_id)
        if (seller_id == netid):
            database.disconnect()
            msg = 'Sorry, you may not bid on an item you are selling.'
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string)
            response = make_response(html)
            return response

        entry = database.get_item(itemid)
        current_price = (entry[0])[3]
        if (float(bid) <= current_price):
            database.disconnect()
            msg = 'Please enter a bid higher than the current price.'
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string)
            response = make_response(html)
            return response
    
        database.bid(itemid, bid, netid)
        entry = database.get_item(itemid)
        database.disconnect()
        msg = 'Your bid has been processed. Thank you!'
        html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string)
        response = make_response(html)
        return response
    else:
        try:
            database = Database()
            database.connect()
            entry = database.get_item(itemid)
            database.disconnect()
            html = render_template('item.html', entry=entry[0], lastSearch=string)
            response = make_response(html)
            return response
        except Exception as e:
            print("error" + str(e), file=stderr)
            exit(1)

#-----------------------------------------------------------------------

@app.route('/itemsold')
def itemsold():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'
    itemid = request.args.get('itemid')

    database = Database()
    database.connect()
    entry = database.get_solditem(itemid)
    database.disconnect()
    html = render_template('itemsold.html', entry=entry[0], errormsg='')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/sell', methods=('GET', 'POST'))
def sell():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    # parse user input for item upload details
    # ***** need to handle other info still *****
    if request.method == 'POST':
        if 'image' not in request.files:
            print("err")
        image = request.files['image']
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
        itemid = int(random.uniform(100, 1000000))
        #if postdate is None:
        postdate = datetime.date.today()
        #if netid is None:
        netid = username

        # connect to database
        database = Database()
        database.connect()
        
        if (image.filename == ''):
            print("none")
            image = ''
            image_read = None
            safefilename = ''
        else:
            print(image)
            safefilename = secure_filename(randstr() + '-' + image.filename)
            imgpath = '{}/{}'.format(IMAGE_DIR_AVAILABLE, safefilename)
            image.save(imgpath)
            image.seek(0)
            image_read = image.read()
            database.add_image(itemid, image_read, safefilename)
            print(database.image_table_size())

        database.add_to_db(itemid, postdate, netid, price, safefilename, description, title)


        # add to bid database with null bidder netid
        database.bid(itemid, price, None)

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
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    if request.method == 'POST':
        
        if (request.form.get('deletebid') is not None):
            delete_bid_itemid = request.form.get('deletebid')
            database = Database()
            database.connect()
            database.remove_bid(delete_bid_itemid, username)

            netid_results = database.get_all_items_from_netid(username)
            bidder_results = database.get_all_items_from_maxbidder(username)

            database.disconnect()

            html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
            response = make_response(html)
            return response

        elif (request.form.get('deleteitem') is not None):
            delete_item_itemid = request.form.get('deleteitem')
            database = Database()
            database.connect()

            delete_item_filename = (database.get_item(delete_item_itemid)[0])[4]

            database.delete_from_db(delete_item_itemid)
            database.delete_from_bids(delete_item_itemid)

            if (delete_item_filename != ''):

                os.remove(os.path.join(IMAGE_DIR_AVAILABLE, delete_item_filename))
                database.delete_image(delete_item_itemid)

            netid_results = database.get_all_items_from_netid(username)
            bidder_results = database.get_all_items_from_maxbidder(username)

            database.disconnect()

            html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
            response = make_response(html)
            return response

        else:
            print("accepted bid!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
            itemid = request.form['accept']
            selldate = datetime.date.today()

            database = Database()
            database.connect()
            entry = database.get_item(itemid)[0]
            max_bid_user = entry[7]
            print("itemid: " + str(itemid))
            current_max_bid = database.get_max_bid(itemid)
            print("current max bid: " + str(current_max_bid))
            current_max_bidder = current_max_bid[1]
            print("max bid user: " + str(max_bid_user))
            print("current max bidder: " + str(current_max_bidder))

            if (max_bid_user == current_max_bidder):
                print("yes!!!!----------------------------------------------")
                database.copy_to_purchased(itemid, selldate, max_bid_user)
                delete_item_filename = (database.get_item(itemid)[0])[4]
                database.delete_from_db(itemid)
                database.delete_from_bids(itemid)
                print("222222222222222222222222222222222222222!!!!----------------------------------------------")
                send_mail(str(current_max_bidder).strip() + '@princeton.edu', str(username).strip() + '@princeton.edu', str(entry[6]), str(current_max_bid[2]))
                if (delete_item_filename != ''):
                    os.rename(os.path.join(IMAGE_DIR_AVAILABLE, delete_item_filename), os.path.join(IMAGE_DIR_PURCHASED, delete_item_filename))
                    database.copy_image_to_purchased_images(itemid)
                    database.delete_image(itemid)

            netid_results = database.get_all_items_from_netid(username)
            bidder_results = database.get_all_items_from_maxbidder(username)

            database.disconnect()

            html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
            response = make_response(html)
            return response

    else:
        database = Database()
        database.connect()
        netid_results = database.get_all_items_from_netid(username)
        bidder_results = database.get_all_items_from_maxbidder(username)

        html = render_template('track.html', netid_results=netid_results, bidder_results=bidder_results)
        response = make_response(html)
        return response

#-----------------------------------------------------------------------

@app.route('/history')
def history():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    database = Database()
    database.connect()
    netid_results = database.get_solditems_from_netid(username)
    bought_results = database.get_boughtitems_from_netid(username)
    database.disconnect()

    html = render_template('history.html', netid_results=netid_results, bought_results=bought_results)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------


@app.route('/redirect_home_control')
@app.route('/index')
@app.route('/')
def home_control():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
        # send_mail("passpi32@gmail.com", "ps21@princeton.edu", "an item", str(235))
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    try:
        database = Database()
        database.connect()
        results = database.get_available_db()
        database.disconnect()

        html = render_template('index.html', results=results, lastSearch='')
        # html = render_template('index.html')
        response = make_response(html)

        # NOTE: deal with cookies
        response.set_cookie('lastSearch', '')
        return response

    except Exception as e:
        print("error" + str(e), file=stderr)
        exit(1)
    
#-----------------------------------------------------------------------

# @app.route('/<int:item_id>', methods=['GET'])
# def get_image_from_db(item_id):
#     database = Database()
#     database.connect()
#     itemid = str(item_id)
#     entry = database.get_item(itemid)
#     item = entry[0]
#     database.disconnect()
#     print("image loaded")
#     return app.response_class(item[4], mimetype='application/octet-stream')

# @app.route('/history_control')
# def history_control():
#     # if 'username' not in session:
#     #     username = CASClient().authenticate().strip()
#     #     check_user(username)
#     # else:
#     #     username = session.get('username').strip()

#     username = 'jjsalama'

#     try:

#         html = render_template('history_view.html')
#         response = make_response(html)
#         return response

#     except Exception as e:
#         print("error" + str(e), file=stderr)
#         exit(1) 

#-----------------------------------------------------------------------


def prep_results(results):

    html = ''
    for entry in results:
        html += '<div class="col-lg-4 col-md-6 mb-4">'
        html += '<div class="card h-100">'
        html += '<a href="item?itemid={}">'.format(entry[0])
        if entry[4] != '':
            html += '<img class="card-img-top" src="/static/images/available/{}" alt="">'.format(entry[4])
        else:
            html += '<img class="card-img-top" src="/static/images/default.png" alt="">'
        html += '</a>'
        html += '<div class="card-body">'
        html += '<h4 class="card-title">'
        html += '<a href="item?itemid={}">{}</a>'.format(entry[0], entry[6])
        html += '</h4>'
        html += '<h5>${}</h5> <p><i>{}</i></p> <p class="card-text">{}</p>'.format(entry[3], entry[1], entry[5])
        # html += '</div> <div class="card-footer"> <p><i>{}</i></p> </div> </div> </div>'.format(entry[2])
        html += '</div> <div class="card-footer"> <p><i>{}</i></p> </div> </div> </div>'.format(entry[2])
    return html
    # {% for entry in results: %}
    #     <div class="col-lg-4 col-md-6 mb-4">
    #       <div class="card h-100">
    #         <a href="item?itemid={{entry[0]}}">
    #           {% if entry[4] != '' %}
    #             <img class="card-img-top" src="/static/images/available/{{entry[4]}}" alt="">
    #           {% else %}
    #             <img class="card-img-top" src="/static/images/default.png" alt="">
    #           {% endif %}
    #         </a>
    #         <div class="card-body">
    #           <h4 class="card-title">
    #             <a href="item?itemid={{entry[0]}}">{{entry[6]}}</a>
    #           </h4>
    #           <h5>${{entry[3]}}</h5>
    #           <p><i>{{entry[1]}}</i></p>
    #           <p class="card-text">{{entry[5]}}</p>
    #         </div>
    #         <div class="card-footer">
    #           <p><i>{{entry[2]}}</i></p>
    #         </div>
    #       </div>
    #     </div>
    # {% endfor %} 




@app.route('/search')
def search():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    try:
        string = request.args.get('string')
        if (string is None) or (string.strip() == ''):
            string = ''
        
        database = Database()
        database.connect()
        results = database.search(string)
        database.disconnect()

        html = render_template('index.html', results=results, lastSearch=string)
        # html = prep_results(results)
        response = make_response(html)

        # NOTE: deal with cookies
        response.set_cookie('lastSearch', string)
        return response
        
    except Exception as e:
        print('error-search(): ' + str(e), file=stderr)
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
