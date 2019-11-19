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
    
    def get_available_db(self):
        cursor = self._connection.cursor()

        cursor.execute("""SELECT * from "available_items";""")
        results = cursor.fetchall()
        
        return results
    
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
    
    def get_all_items_from_maxbidder(self, maxbidder):
        cursor = self._connection.cursor()
        
        # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE MAX_BID_USER=\'"""+maxbidder+"\';")
        results = cursor.fetchall()
        
        return results

    
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

    def add_to_db(self, itemid, postdate, netid, price, image, description, title):
        cursor = self._connection.cursor()
        entry = [itemid, postdate, netid, price, image, description, title]
        postgres_insert_query = """ INSERT INTO "available_items" 
        (ITEM_ID, POST_DATE, SELLER_NETID, PRICE, IMAGE, DESCRIPTION, TITLE) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])
        cursor.execute(postgres_insert_query, record_to_insert)
        self._connection.commit()

    def set_max_bid(self, max_bid, max_bid_user):
        cursor = self._connection.cursor()

#---------------------------------------------------------------------

if __name__ == '__main__':
    #get_image(13)
    #add_pic_db()
    #add_to_db()
    #delete_from_db(19)
    database1 = Database()
    database1.connect()
    #database1.add_to_db(1162, "2019-11-15", "jjsalama", 9999, None, "unbelievably cool thing", "Cool water bottle")
    #database1.delete_from_db(1162)

    #print(database1.get_all_items_from_netid("carinal"))
    #get_available_db()