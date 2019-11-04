import psycopg2


def add_to_db():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "Super123",
                                      host = "localhost",
                                      port = "5432",
                                      database = "retail_db")

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
        #     postgres_insert_query = """ INSERT INTO "User_Info" (NETID) VALUES (%s)"""
        #     record_to_insert = (netid,)
        #     cursor.execute(postgres_insert_query, record_to_insert)

        #     connection.commit()
        #     count = cursor.rowcount
        #     print (count, "Record inserted successfully into mobile table")

        # insert sample available items into table
        item_data = [[1, '2019-11-04', 'ps21', 2, None, 'animal crackers', 'crackers'], 
        [2, '2019-11-03', 'pablob', 341, None, 'live animal', 'elephant'], 
        [3, '2019-11-02', 'carinal', 10, None, 'pet animal', 'animal']]
        for entry in item_data:
            postgres_insert_query = """ INSERT INTO "Available_Items" 
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
