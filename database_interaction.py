import psycopg2

user = "cbunmfgzjtkxmr"
host = "ec2-174-129-253-180.compute-1.amazonaws.com"
pwd = "9f9ace5a8c31729f9643ff953c5cde217ee7ccc9c9ad87e91fecad55eb2bb282"
port = "5432"
db = "d6om41i3v32f"
# web: gunicorn reTail_server:app
# release: python database_interaction.py

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

#---------------------------------------------------------------------
#---------------------------------------------------------------------
#---------------------------------------------------------------------










#---------------------------------------------------------------------
# in progress features
#---------------------------------------------------------------------
def get_image(item_id):
    try:
        entry = get_item(str(13))
        #print(entry)
        #img = open(r"C:\Users\paska\OneDrive\Documents\Princeton\Fall 2019\COS333\Final_Project\Repo\reTailVCR\dog_test_out.jpg", "wb")
        # print(bytearray.fromhex(str(bytes(entry[0][4]))))

        temp = bytes(entry[0][4])
        print(temp[0:100])
        #print(entry[0][4])
        #img.write()
        #img.close

        # path_to_file = r"C:\Users\paska\OneDrive\Documents\Princeton\Fall 2019\COS333\Final_Project\Repo\reTailVCR\dog_test.jpg"
        # drawing = open(path_to_file, 'rb').read()
        # print(drawing)
        # img = open(r"C:\Users\paska\OneDrive\Documents\Princeton\Fall 2019\COS333\Final_Project\Repo\reTailVCR\dog_test_out.jpg", "wb")
        # img.write(drawing)
        # img.close

    except Exception as e:
        print (e)


def add_pic_db():
    try:
        path_to_file = r"C:\Users\paska\OneDrive\Documents\Princeton\Fall 2019\COS333\Final_Project\Repo\reTailVCR\dog_test.jpg"
        drawing = open(path_to_file, 'rb').read()
        blob = psycopg2.Binary(drawing)
        print(blob)
        connection = psycopg2.connect(user = user,
                                      password = pwd,
                                      host = host,
                                      port = port,
                                      database = db)

        cursor = connection.cursor()
       

        entry = [14, '2019-11-12', 'ps21', 34, drawing, 'inserting dog image into db', 'dog image test']

        postgres_insert_query = """ INSERT INTO "available_items" 
            (ITEM_ID, POST_DATE, SELLER_NETID, PRICE, IMAGE, DESCRIPTION, TITLE) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        
        record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()

        

        # results = cursor.fetchall()

        # return results   

    except (Exception, psycopg2.Error) as error:
        print ("Error while connecting to PostgreSQL", error)

    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# get all available items from Database
def get_available_db():
    try:
        connection = psycopg2.connect(user = user,
                                      password = pwd,
                                      host = host,
                                      port = port,
                                      database = db)

        cursor = connection.cursor()
       
        cursor.execute("""SELECT * from "available_items";""")
        results = cursor.fetchall()

        return results   

    except (Exception, psycopg2.Error) as error:

        print ("Error while connecting to PostgreSQL", error)

    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


#---------------------------------------------------------------------

# sample function showing logic for adding to database
def add_to_db():
    try:
        connection = psycopg2.connect(user = user,
                                      password =pwd,
                                      host = host,
                                      port = port,
                                      database = db)

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print (connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        # insert sample netids into table
        user_data = ['ps21', 'pablob', 'carinal', 'jjsalama', 'ilenee']
        # for netid in user_data:
        #     postgres_insert_query = """ INSERT INTO "users" (NETID) VALUES (%s)"""
        #     record_to_insert = (netid,)
        #     cursor.execute(postgres_insert_query, record_to_insert)

        #     connection.commit()
        #     count = cursor.rowcount
        #     print (count, "Record inserted successfully into mobile table")

        # insert sample available items into table
        item_data = [[1, '2019-11-04', 'ps21', 2, None, 'animal crackers', 'crackers'], 
        [2, '2019-11-03', 'pablob', 341, None, 'live animal', 'elephant'], 
        [3, '2019-11-02', 'carinal', 10, None, 'pet animal', 'animal'], 
        [4, '2019-11-06', 'ilene', 100, None, 'black red blue', 'colors'], 
        [5, '2019-11-02', 'jjsalama', 13, None, ' items for sale stuff words', 'toys'], 
        [2, '2019-11-02', 'test', 13, None, ' duplicate id', 'bad']]
        for entry in item_data:
            postgres_insert_query = """ INSERT INTO "available_items" 
            (ITEM_ID, POST_DATE, SELLER_NETID, PRICE, IMAGE, DESCRIPTION, TITLE) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])
            cursor.execute(postgres_insert_query, record_to_insert)

            connection.commit()
            count = cursor.rowcount
            print (count, "Record inserted successfully into mobile table")

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#---------------------------------------------------------------------

def delete_from_db(itemId):
    try:
        connection = psycopg2.connect(user = user,
                                      password =pwd,
                                      host = host,
                                      port = port,
                                      database = db)

        cursor = connection.cursor()

        postgres_delete_query = """ DELETE FROM "available_items" WHERE ITEM_ID = %s """
        record_to_delete = (itemId, )
        cursor.execute(postgres_delete_query, record_to_delete)

        connection.commit()
        count = cursor.rowcount
        print (count, "Record deleted successfully from table")

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#---------------------------------------------------------------------

def get_item(itemid):
    try:
        connection = psycopg2.connect(user = user,
                                      password = pwd,
                                      host = host,
                                      port = port,
                                      database = db)

        cursor = connection.cursor()
       
       # NOTE: Shouldn't this be a prepared statement?
        cursor.execute("""SELECT * from "available_items" WHERE item_id="""+itemid+";")
        entry = cursor.fetchall()

        return entry   

    except (Exception, psycopg2.Error) as error:

        print ("Error while connecting to PostgreSQL", error)

    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == '__main__':
    #get_image(13)
    #add_pic_db()
    #add_to_db()
    #delete_from_db(19)
    database1 = Database()
    database1.connect()
    #database1.add_to_db(1162, "2019-11-15", "jjsalama", 9999, None, "unbelievably cool thing", "Cool water bottle")
    database1.delete_from_db(1162)
    #get_available_db()

