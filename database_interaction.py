import psycopg2

user = "cbunmfgzjtkxmr"
host = "ec2-174-129-253-180.compute-1.amazonaws.com"
pwd = "9f9ace5a8c31729f9643ff953c5cde217ee7ccc9c9ad87e91fecad55eb2bb282"
port = "5432"
db = "d6om41i3v32f"
# Host
# ec2-174-129-253-180.compute-1.amazonaws.com
# Database
# d6om41i3v32f
# User
# cbunmfgzjtkxmr
# Port
# 5432
# Password
# 9f9ace5a8c31729f9643ff953c5cde217ee7ccc9c9ad87e91fecad55eb2bb282
# URI
# postgres://cbunmfgzjtkxmr:9f9ace5a8c31729f9643ff953c5cde217ee7ccc9c9ad87e91fecad55eb2bb282@ec2-174-129-253-180.compute-1.amazonaws.com:5432/d6om41i3v32f
# Heroku CLI
# heroku pg:psql postgresql-animated-99582 --app re-tail

#---------------------------------------------------------------------

class Database:

    def __init__(self):
        self._connection = None
    
    def connect(self):
        self._connection = psycopg2.connect(user = user,
                                            password = pwd,
                                            host = host,
                                            port = port,
                                            database = db)
    
    def disconnect(self):
        if self._connection:
            self._connection.close()
    
    def user_exists(self, netid):
        cursor = self._connection.cursor()
        cursor.execute("""SELECT * from "users" WHERE netid = %s;""", (netid, ))
        user = cursor.fetchone()

        if user is None:
            return False
        return True
    
    def add_user(self, netid):
        cursor = self._connection.cursor()
        cursor.execute(""" INSERT INTO "users" (NETID) VALUES (%s);""", (netid, ))
        self._connection.commit()
        
    
    #---------------------------------------------------------------------
    # getting from db functions

    def get_user(self, netid):
        cursor = self._connection.cursor()
        cursor.execute("""SELECT * from "users" WHERE netid = %s;""", (netid, ))

        return cursor.fetchone()

    def get_available_db(self):
        cursor = self._connection.cursor()

        cursor.execute("""SELECT * from "available_items";""")
        results = cursor.fetchall()
        
        return results
    
    def check_exists_item(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT EXISTS(SELECT 1 from "available_items" WHERE item_id="""+itemid+");")
        exists = cursor.fetchone()[0]
        
        return exists

    def get_item(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE item_id="""+itemid+";")
        entry = cursor.fetchall()
        
        return entry

    def get_all_items_from_netid(self, netid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE SELLER_NETID=\'"""+netid+"\';")
        results = cursor.fetchall()
        
        return results

    def get_activeitems_from_netid(self, netid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE MAX_BID_USER IS NOT NULL AND SELLER_NETID=\'"""+netid+"\';")
        results = cursor.fetchall()
        
        return results
    
    def get_all_items_from_maxbidder(self, maxbidder):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE MAX_BID_USER=\'"""+maxbidder+"\';")
        results = cursor.fetchall()
        
        return results

    def get_available_images(self):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "images" """)
        results = cursor.fetchall()
        return results

    def get_purchased_images(self):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "purchased_images" """)
        results = cursor.fetchall()
        return results

    def get_image(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "images" WHERE item_id="""+itemid+";")
        entry = cursor.fetchall()
        imaga_data = entry[1]
        
        return imaga_data

    def image_table_size(self):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT pg_size_pretty( pg_total_relation_size('images') )""")
        entry = cursor.fetchall()
        size = entry[0]
        return size

    #---------------------------------------------------------------------
    # functions for the purchase history 
    
    def get_solditems_from_netid(self, netid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "purchased_items" WHERE SELLER_NETID=\'"""+netid+"\';")
        results = cursor.fetchall()

        return results
    
    def get_solditem(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "purchased_items" WHERE item_id="""+itemid+";")
        entry = cursor.fetchall()
        
        return entry

    def check_exists_solditem(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT EXISTS(SELECT 1 from "purchased_items" WHERE item_id="""+itemid+");")
        exists = cursor.fetchone()[0]
        return exists

    def get_boughtitems_from_netid(self, netid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "purchased_items" WHERE BUYER_NETID=\'"""+netid+"\';")
        results = cursor.fetchall()
        
        return results

    def add_to_purchased(self, itemid, selldate, price, img_filename, seller_netid, buyer_netid, title, description):
        cursor = self._connection.cursor()
        #image = psycopg2.Binary(image)
        entry = [itemid, selldate, price, img_filename, seller_netid, buyer_netid, title, description]
        postgres_insert_query = """ INSERT INTO "purchased_items" 
        (ITEM_ID, SELL_DATE, PRICE, IMG_FILENAME, SELLER_NETID, BUYER_NETID, TITLE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7])
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    def copy_to_purchased(self, itemid, selldate, buyer_netid):
        cursor = self._connection.cursor()
        cursor.execute("""SELECT * from "available_items" WHERE item_id="""+itemid+";")
        entry_available = cursor.fetchone()

        seller_netid = entry_available[2]
        price = entry_available[3]
        img_filename = entry_available[4]
        description = entry_available[5]
        title = entry_available[6]
        
        entry = [itemid, selldate, price, img_filename, seller_netid, buyer_netid, title, description]
        postgres_insert_query = """ INSERT INTO "purchased_items" 
        (ITEM_ID, SELL_DATE, PRICE, IMG_FILENAME, SELLER_NETID, BUYER_NETID, TITLE, DESCRIPTION) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7])
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    def copy_image_to_purchased_images(self, itemid):
        cursor = self._connection.cursor()
        cursor.execute("""SELECT * from "images" WHERE item_id="""+itemid+";")
        entry = cursor.fetchone()

        image_data = entry[1]
        img_filename = entry[2]

        purchased_entry = [itemid, image_data, img_filename]
        
        postgres_insert_query = """ INSERT INTO "purchased_images" (ITEM_ID, IMG_DATA, IMG_FILENAME) VALUES (%s,%s,%s)"""
        
        record_to_insert = (itemid, image_data, img_filename)
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    #---------------------------------------------------------------------
    # major db functions

    def add_to_db(self, itemid, postdate, netid, price, img_filename, description, title):
        cursor = self._connection.cursor()
        #image = psycopg2.Binary(image)
        entry = [itemid, postdate, netid, price, img_filename, description, title]
        postgres_insert_query = """ INSERT INTO "available_items" 
        (ITEM_ID, POST_DATE, SELLER_NETID, PRICE, IMG_FILENAME, DESCRIPTION, TITLE, INITIAL_PRICE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[3])
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    def delete_from_db(self, itemid):
        cursor = self._connection.cursor()

        postgres_delete_query = """ DELETE FROM "available_items" WHERE ITEM_ID = %s """
        record_to_delete = (itemid, )
        cursor.execute(postgres_delete_query, record_to_delete)

        self._connection.commit()

    def search(self, string):
        cursor = self._connection.cursor()

        query_string = '%' + string + '%'

        postgres_search_string = """SELECT * FROM "available_items" WHERE (description ILIKE %s) OR (title ILIKE %s);"""
        string_to_search = (query_string, query_string)
        cursor.execute(postgres_search_string, string_to_search)

        results = cursor.fetchall()
        return results

    def add_image(self, itemid, image_data, img_filename):
        cursor = self._connection.cursor()
        #binary_image = psycopg2.Binary(image_data)

        postgres_insert_query = """ INSERT INTO "images" (ITEM_ID, IMG_DATA, IMG_FILENAME) VALUES (%s,%s,%s)"""
        
        record_to_insert = (itemid, image_data, img_filename)
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    def delete_image(self, itemid):
        cursor = self._connection.cursor()

        postgres_delete_query = """ DELETE FROM "images" WHERE ITEM_ID = %s """
        record_to_delete = (itemid, )
        cursor.execute(postgres_delete_query, record_to_delete)

        self._connection.commit()

    #---------------------------------------------------------------------
    # bidding functions

    def bid(self, itemid, max_bid, max_bid_user):
        cursor = self._connection.cursor()
        bid_entry = [itemid, max_bid, max_bid_user]

        postgres_select_query = """SELECT * from "available_items" WHERE item_id = %s"""
        record_to_select = (bid_entry[0], )
        cursor.execute(postgres_select_query, record_to_select)
        
        if (cursor.fetchone() is None):
            print("none")
            return

        cursor = self._connection.cursor()
        cursor.execute(postgres_select_query, record_to_select)
        entry = cursor.fetchall()[0]
        current_price = entry[3]

        current_bid = float(max_bid)
        seller_netid = entry[2]

        postgres_insert_query = """ INSERT INTO "bids" (ITEM_ID, BIDDER_NETID, BID) VALUES (%s,%s,%s)"""
        record_to_insert = (itemid, max_bid_user, max_bid)
        cursor.execute(postgres_insert_query, record_to_insert)
        
        postgres_update_query = """UPDATE "available_items" SET price = %s, max_bid_user = %s WHERE ITEM_ID = %s;"""
        record_to_update = (max_bid, max_bid_user, itemid)
        cursor.execute(postgres_update_query, record_to_update)
        self._connection.commit()

    def remove_bid(self, itemid, max_bid_user):
        cursor = self._connection.cursor()

        # delete from bids database
        postgres_delete_query = """ DELETE FROM "bids" WHERE ITEM_ID = %s AND BIDDER_NETID = %s"""
        record_to_delete = (itemid, max_bid_user)
        cursor.execute(postgres_delete_query, record_to_delete)
        print("deleting")
        self._connection.commit()

        # select in descending order the remaining bids
        cursor = self._connection.cursor()
        postgres_select_query = """ SELECT * from "bids" WHERE ITEM_ID = %s ORDER BY BID DESC"""
        record_to_select = (itemid, )
        cursor.execute(postgres_select_query, record_to_select)

        # if (cursor.fetchone() is None):
        #     print("none left")
        #     cursor = self._connection.cursor()
        #     postgres_update_query = """UPDATE "available_items" SET price = initial_price, max_bid_user = %s WHERE ITEM_ID = %s;"""
        #     record_to_update = (None, itemid)
        #     cursor.execute(postgres_update_query, record_to_update)
        #     self._connection.commit()
        if (cursor.fetchone() is not None):
            cursor = self._connection.cursor()
            cursor.execute(postgres_select_query, record_to_select)
            new_max_bid = cursor.fetchall()[0]

            cursor = self._connection.cursor()
            postgres_update_query = """UPDATE "available_items" SET price = %s, max_bid_user = %s WHERE ITEM_ID = %s;"""
            record_to_update = (new_max_bid[2], new_max_bid[1], new_max_bid[0])
            cursor.execute(postgres_update_query, record_to_update)
            self._connection.commit()
    
    def delete_from_bids(self, itemid):
        cursor = self._connection.cursor()

        postgres_delete_query = """ DELETE FROM "bids" WHERE ITEM_ID = %s"""
        record_to_delete = (itemid, )
        cursor.execute(postgres_delete_query, record_to_delete)
        self._connection.commit()

    def get_item_bids(self, itemid):
        cursor = self._connection.cursor()

        postgres_select_query = """ SELECT * FROM "bids" WHERE ITEM_ID = %s"""
        item_to_find = (itemid, )
        cursor.execute(postgres_select_query, item_to_find)
        bids = cursor.fetchall()
        return bids


    def get_max_bid(self, itemid):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        postgres_select_query = """ SELECT * from "bids" WHERE ITEM_ID = %s ORDER BY BID DESC"""
        record_to_select = (itemid, )
        cursor.execute(postgres_select_query, record_to_select)
        result = cursor.fetchall()[0]
        return result

#---------------------------------------------------------------------
#---------------------------------------------------------------------
#---------------------------------------------------------------------

# if __name__ == '__main__':
    #get_image(13)
    #add_pic_db()
    #add_to_db()
    #delete_from_db(19)
    #database1 = Database()
    #database1.connect()
    # database = Database()
    # database.connect()
    # entry = database.get_item('14')
    # max_bid_user = (entry[0])[7]
    # print(max_bid_user)

    # database.copy_to_purchased('14', '2019-11-19', max_bid_user)
    # print(database.get_boughtitems_from_netid('carinal'))
    #database1.add_to_db(1162, "2019-11-15", "jjsalama", 9999, None, "unbelievably cool thing", "Cool water bottle")
    #database1.delete_from_db(1162)

    #print(database1.get_all_items_from_netid("carinal"))
    #get_available_db()