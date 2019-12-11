#-------------------------------------------------------------------------
# user.py
# Data type for a user of the website
# Project: reTail
# Author: Pablo Bickenbach
#-------------------------------------------------------------------------

class User:

    def __init__(self, netid, email, first_name, last_name):
        self._netid = netid
        self._email = email 
        self._first_name = first_name
        self._last_name = last_name

    def __str__(self):
        return f'Neitd: {self._netid}\nEmail: {self._email}\nFirst Name: {self._first_name}\nLast Name: {self._last_name}'
    
    def get_netid(self):
        return self._netid
    
    def get_email(self):
        return self._email
    
    def get_first_name(self):
        return self._first_name
    
    def get_last_name(self):
        return self._last_name