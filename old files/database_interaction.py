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
        [3, '2019-11-02', 'jjsalama', 13, None, ' items for sale stuff words', 'toys']]
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

if __name__ == '__main__':
    add_to_db()
    #get_available_db()

