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
import requests
import os
from json import dumps

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

# a list used to store randomly generated itemids while they
# are being used by listings in available_items
# once listing is deleted or sold, the id is removed
itemid_hashset = []

# session objects to speed up remote API calls
s1 = requests.Session()
s2 = requests.Session()

# merriam webster api_key
# change b4 deploying
key = "***"


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

def send_purchase_mail(buyer, seller, item, price):
    try: 

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
        print("send_purchase_mail error: " + str(e))
        # do some other stuff so the people are informed.
        return


#-----------------------------------------------------------------------

def send_modify_mail(bidders, item, itemid):
    try:
        bidder_emails = []
        for bid in bidders:
            if (bid[1] != None):
                bidder_emails.append("{}@princeton.edu".format(bid[1].rstrip()))

        msg = Message(subject="reTail: Item Change Notification!", sender=app.config.get("MAIL_USERNAME"), 
            recipients=bidder_emails, body='The listing for the item, "{}", has been modified, so we removed your bid on it.\n\n\
            If you want to take a look at the modified listing, here\'s a link: https://re-tail.herokuapp.com/item&itemid={}\n\n\
            Thanks for using reTail!'.format(item, itemid))
        mail.send(msg)
    except Exception as e:
        print("send_modify_mail error: " + str(e))
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


@app.route('/modify_item', methods=('GET', 'POST'))
def modify_item():
    print("server reached")
    print(request)
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()


    database = Database()
    database.connect()
    itemid = None

    if (request.method == "GET" and request.args.get('modify') != None):
        print("get reached")
        itemid = request.args.get('modify')
        print("itemid: " + str(itemid))
        print(request)
        entry = (database.get_item(itemid))[0]
        html = render_template('modify_item.html', entry=entry)
        response = make_response(html)
        return response
        # a confirm_change button (let them know it will reset bids), a cancel button (redirect to track page)
            # confirm_change redirects back here, with a get_request
    elif (request.method == "POST" and request.form['item_id'] != None):
        print("post reached")
        title = request.form['title']
        print("title")
        image = request.files['image']
        print(image)
        print("img")
        description = request.form['description']
        print("desc")
        price = request.form['price']
        print("pr")
        tag = request.form['tag']
        print("tag")
        postdate = datetime.date.today()
        netid = username
        old_item_id = request.form['item_id']
        print("id")
        # new_item_id = int(random.uniform(100, 1000000))
        # error handling on the above in case it comes from a non web browser source
        print("getting stuff reached")


        prev_info = (database.get_item(old_item_id))[0]

        # send e-mail to bidders before deleting the bids
        item_bids = database.get_item_bids(old_item_id) 
        send_modify_mail(item_bids, prev_info[6], old_item_id)
        database.delete_from_bids(old_item_id)

        # delete the old item entry data
        database.delete_from_db(old_item_id)

        new_img_bool = True
        
        # if new image is null and previous image is not null
        if image.filename == '' and prev_info[4] != '': 
            safefilename = prev_info[4]
            new_img_bool = False

        print("db stuff")
        # insert the new image into the db
        if new_img_bool == True:
            # delete the old image if there was one
            if (prev_info[4] != ''):
                os.remove(os.path.join(IMAGE_DIR_AVAILABLE, prev_info[4]))
                database.delete_image(old_item_id)

            if (image.filename == ''):
                image = ''
                image_read = None
                safefilename = ''
            else:
                # print(image)
                safefilename = secure_filename(randstr() + '-' + image.filename)
                imgpath = '{}/{}'.format(IMAGE_DIR_AVAILABLE, safefilename)
                image.save(imgpath)
                image.seek(0)
                image_read = image.read()
                database.add_image(old_item_id, image_read, safefilename)
            # print(database.image_table_size())

        # add new db info for the item
        database.add_to_db(old_item_id, postdate, netid, price, safefilename, description, title, tag)

        # add to bid database with null bidder netid
        database.bid(old_item_id, price, None)
        print("work done")
        return redirect("/item?itemid={}".format(old_item_id))
            
    else:
        return redirect('/index')

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
    maxP = request.cookies.get('maxPrice')
    if maxP is None:
        maxP = ''
    minP = request.cookies.get('minPrice')
    if minP is None:
        minP = ''
    ntags = request.cookies.get('ntags')

    tags = []
    for i in range(int(ntags)):
        tags.append(request.cookies.get(f'tag{i + 1}'))
    
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
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string, maxPrice=maxP, minPrice=minP, tags=tags)
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
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string, maxPrice=maxP, minPrice=minP, tags=tags)
            response = make_response(html)
            return response

        entry = database.get_item(itemid)
        current_price = (entry[0])[3]
        if (float(bid) <= current_price):
            database.disconnect()
            msg = 'Please enter a bid higher than the current price.'
            html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string, maxPrice=maxP, minPrice=minP, tags=tags)
            response = make_response(html)
            return response
    
        database.bid(itemid, bid, netid)
        entry = database.get_item(itemid)
        database.disconnect()
        msg = 'Your bid has been processed. Thank you!'
        html = render_template('item.html', entry=entry[0], msg=msg, lastSearch=string, maxPrice=maxP, minPrice=minP, tags=tags)
        response = make_response(html)
        return response
    else:
        try:
            database = Database()
            database.connect()
            entry = database.get_item(itemid)
            database.disconnect()
            html = render_template('item.html', entry=entry[0], lastSearch=string, maxPrice=maxP, minPrice=minP, tags=tags)
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
        print("sell: " + str(request))
        if 'image' not in request.files:
            print("err")
        image = request.files['image']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        tag = request.form['tag']

        if title is None:
            title = ''
        if description is None:
            description = ''
        if price is None:
            price = ''

        # generate a random itemid until you get one that isn't
        # in the itemdid_hashet, meaning that it isn't already being
        # used by an item in available_items 
        itemid = int(random.uniform(100, 1000000))
        while str(itemid) in itemid_hashset:
            itemid = int(random.uniform(100, 1000000))
        itemid_hashset.append(str(itemid))

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

        database.add_to_db(itemid, postdate, netid, price, safefilename, description, title, tag)


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
    print("arriveddddddddddddddddddd!!!!!!!!!!!!!!!!!!!")
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'
    database = Database()
    database.connect()

    if request.method == 'POST':
        print("arrived at POSTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        if (request.form.get('deletebid') is not None):
            delete_bid_itemid = request.form.get('deletebid')
            
            database.remove_bid(delete_bid_itemid, username)            

        elif (request.form.get('deleteitem') is not None):
            delete_item_itemid = request.form.get('deleteitem')           

            if (len(database.get_item(delete_item_itemid)) > 0):
                delete_item_filename = (database.get_item(delete_item_itemid)[0])[4]
                if (delete_item_filename != ''):

                    os.remove(os.path.join(IMAGE_DIR_AVAILABLE, delete_item_filename))
                    database.delete_image(delete_item_itemid)

            database.delete_from_db(delete_item_itemid)
            database.delete_from_bids(delete_item_itemid)
            if str(delete_item_itemid) in itemid_hashset:
                itemid_hashset.remove(str(delete_item_itemid))

        else:
            # print("accepted bid!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
            itemid = request.form['accept']
            selldate = datetime.date.today()

            
            entry = database.get_item(itemid)[0]
            max_bid_user = entry[7]
            print("itemid: " + str(itemid))
            current_max_bid = database.get_max_bid(itemid)
            print("current max bid: " + str(current_max_bid))
            current_max_bidder = current_max_bid[1]
            print("max bid user: " + str(max_bid_user))
            print("current max bidder: " + str(current_max_bidder))

            if (max_bid_user == current_max_bidder):
                # print("yes!!!!----------------------------------------------")
                database.copy_to_purchased(itemid, selldate, max_bid_user)
                delete_item_filename = (database.get_item(itemid)[0])[4]
                database.delete_from_db(itemid)
                database.delete_from_bids(itemid)
                # print("222222222222222222222222222222222222222!!!!----------------------------------------------")
                send_purchase_mail(str(current_max_bidder).strip() + '@princeton.edu', str(username).strip() + '@princeton.edu', str(entry[6]), str(current_max_bid[2]))
                if (delete_item_filename != ''):
                    os.rename(os.path.join(IMAGE_DIR_AVAILABLE, delete_item_filename), os.path.join(IMAGE_DIR_PURCHASED, delete_item_filename))
                    database.copy_image_to_purchased_images(itemid)
                    database.delete_image(itemid)

                if str(itemid) in itemid_hashset:
                    itemid_hashset.remove(str(itemid))

    if request.args.get('action') == None:
        print("first arrivalllllllllll")
        html = render_template('track.html')
        response = make_response(html)
        return response
    else:

        netid_results = database.get_all_items_from_netid(username)
        bidder_results = database.get_all_items_from_maxbidder(username)

        database.disconnect()

        results = []
        sell_list = []
        for item in netid_results:
            item_dict = {"item_id":str(item[0]), "price":str(item[3]), 
            "item_title":str(item[6]), "max_bidder":str(item[7])}
            sell_list.append(item_dict)
        results.append(sell_list)

        bid_list = []
        for item in bidder_results:
            item_dict = {"item_id":str(item[0]), "price":str(item[3]),
             "item_title":str(item[6])}
            bid_list.append(item_dict)
        results.append(bid_list)
        print("results: " + str(results))

        jsonStr = dumps(results)
        response = make_response(jsonStr)
        response.headers['Content-Type'] = 'application/json'
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
        # send_purchase_mail("passpi32@gmail.com", "ps21@princeton.edu", "an item", str(235))
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    try:
        database = Database()
        database.connect()
        results = database.get_available_db()
        database.disconnect()

        html = render_template('index.html', results=results, lastSearch='', maxPrice='', minPrice='', tags=[])
        # html = render_template('index.html')
        response = make_response(html)

        # NOTE: deal with cookies
        response.set_cookie('lastSearch', '')
        response.set_cookie('maxPrice', '')
        response.set_cookie('minPrice', '')
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

def search_helper(query):
    try:
        # merriam webster api key
        # parse query
        query_words = query.split(" ")
        for word in query_words:
            if word == "a":
                query_words.remove(word)
            elif word == "the": 
                query_words.remove(word)
            elif word == "for": 
                query_words.remove(word)
            elif word == "of": 
                query_words.remove(word)
            elif word == "an": 
                query_words.remove(word)
            elif word == "on": 
                query_words.remove(word)
            elif word == "by": 
                query_words.remove(word)

        # find nouns in query
        nouns = []
        #start = time.time()
        for word in query_words:
            req = s1.get("https://dictionaryapi.com/api/v3/references/thesaurus/json/{}?key={}".format(word, key))
            
            defs = req.json()

            if len(defs) == 0:
                continue
            elif type(defs[0]) is not dict:
                # print("w: " + word)
                query_words.append(defs[0])
                if len(defs) > 1: 
                    query_words.append(defs[1])
                nouns.append(word) ## might not be a noun, but could be a common/colloquial word
            elif defs[0]['fl'] == 'noun' or defs[0]['fl'] == 'plural noun':
                # nouns.append(defs[0]['meta']['id'])
                nouns.append(word)
            else:
                print("error")

        #print(time.time() - start)

        nouns2 = []
        for n in nouns:
            nouns2.append(n.split(":")[0])

        # get synonyms
        print(nouns2)
        nouns = []
        for n in nouns2:
            nouns.append(n)
            req = s2.get("https://api.datamuse.com/words?ml={}&topics=item&md=p".format(n))
            syns = req.json()

            if len(syns) < 6: 
                size = len(syns)
            else:
                size = 6
            for i in range(size):
                if 'n' in syns[i]['tags']:
                    nouns.append(syns[i]['word'])

        print(nouns)
        return nouns
    except Exception as e:
        print("search_helper exception: " + str(e))
        return []

@app.route('/search')
def search():
    if 'username' not in session:
        username = CASClient().authenticate().strip()
        check_user(username)
    else:
        username = session.get('username').strip()

    #username = 'jjsalama'

    try:
        query = request.args.get('query')
        # print ("query: " + str(query))
        query = query.strip()
        maxP = request.args.get('maxprice')
        minP = request.args.get('minprice')
        tags = request.args.getlist('tag')

        set_max_cookie = True
        set_min_cookie = True

        if (query is None) or (query.strip() == ''):
            query = ''

        # setting it to a number larger than all possible entries on the site
        if (maxP is None) or (maxP.strip() == ''):
            maxP = '99999999999'
            set_max_cookie = False
        # setting it to lowest possible entry
        if (minP is None) or (minP.strip() == ''):
            minP = '0'
            set_min_cookie = False

        database = Database()
        database.connect()
        print('pre search')

        nlp_nouns = []
        if query != '':
            nlp_nouns = search_helper(query)

        results = database.search(query, maxP, minP, tags, nlp_nouns)
        database.disconnect()
        print('post search')

        if not set_max_cookie:
            maxP = ''
        
        if not set_min_cookie:
            minP = ''

        html = render_template('index.html', results=results, lastSearch=query, maxPrice=maxP, minPrice=minP, tags=tags)
        # html = prep_results(results)
        response = make_response(html)
        print('post response')


        # NOTE: deal with cookies
        response.set_cookie('lastSearch', query)
        response.set_cookie('maxPrice', maxP)
        response.set_cookie('minPrice', minP)
        response.set_cookie('ntags', str(len(tags)))
        for i in range(len(tags)):
            response.set_cookie(f'tag{i + 1}', tags[i])
        return response
        
    except Exception as e:
        print('error-search(): ' + str(e), file=stderr)
        exit(1)

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

if __name__ == '__main__':
    # if len(argv) != 2:
    #     print('Usage: ' + argv[0] + ' port')
    #     exit(1)
    # # add things to db
    # # 
    # app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
    app.run()