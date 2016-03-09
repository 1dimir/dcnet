#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quick implementation of danceconvention.net API
Visit https://github.com/danceconvention/dcnet-public/wiki/REST-API for detailed specification
"""

__author__ = "Dmitry Sorokin"

import requests
import json
from bs4 import BeautifulSoup


DCNET_URL = "http://danceconvention.net/eventdirector/rest/eventinfo/"
EVENTPAGE_URL_TEMPLATE = "http://danceconvention.net/eventdirector/{language}/eventpage/{contest}"
RESOURCES = {
    'contests': "{}{{}}/contests".format(DCNET_URL),
    'signups': "{}{{}}/signups".format(DCNET_URL),
    'leaders': "{}signups/{{}}/leaders".format(DCNET_URL),
    'followers': "{}signups/{{}}/follows".format(DCNET_URL),
    'couples': "{}signups/{{}}/couples".format(DCNET_URL),
    'seeking leaders': "{}signups/{{}}/seeking/leaders".format(DCNET_URL),
    'seeking followers': "{}signups/{{}}/seeking/follows".format(DCNET_URL)
}

def get_collection(resource_name, collection_id):

    if not resource_name in RESOURCES:
        return None

    resource_url = RESOURCES.get(resource_name).format(collection_id)

    response = requests.get(resource_url)
    
    if response.status_code != 200:
        return None

    return json.loads(response.text, 'UTF-8')


class Event(object):
    """
    Event object
    """

    def __init__(self, id=None):
        self._id = id
        self._valid = None
        self.signups = None
        self.contests = None
        self._description = None
    
    
    @property
    def id(self):
        return self._id
    
    
    @property
    def valid(self):
        if self._valid is None:
            self.load_contests()

        return bool(self._valid)

    @property
    def description(self):
        return self._description
    

    def load_contests(self):
        self.contests = {x.get('id'): x for x in get_collection('contests', self._id)}
        self._valid = bool(self.contests)
    

    def load_signups(self):
        self.signups = {x.get('participantId'): x for x in get_collection('signups', self._id)}
    
    
    def load_leaders(self, contest_id):
        
        if not contest_id in self.contests:
            return

        self.contests[contest_id]['leaders'] = get_collection('leaders', contest_id)


    def load_followers(self, contest_id):
        
        if not contest_id in self.contests:
            return

        self.contests[contest_id]['followers'] = get_collection('followers', contest_id)


    def load_couples(self, contest_id):
        
        if not contest_id in self.contests:
            return

        self.contests[contest_id]['couples'] = get_collection('couples', contest_id)

    
    def load_seeking_leaders(self, contest_id):

        if not contest_id in self.contests:
            return

        self.contests[contest_id]['seeking leaders'] = get_collection('seeking leaders', contest_id)
        

    def load_seeking_followers(self, contest_id):
        
        if not contest_id in self.contests:
            return

        self.contests[contest_id]['seeking followers'] = get_collection('seeking followers', contest_id)

    
    def load_contest(self, contest_id):

        if not contest_id in self.contests:
            return

        divisionType = self.contests[contest_id].get('divisionType', '').upper()
 
        if divisionType  == 'RANDOM_PARTNER':
            self.load_leaders(contest_id)
            self.load_followers(contest_id)
            self.load_seeking_leaders(contest_id)
            self.load_seeking_followers(contest_id)

        elif divisionType == 'OPEN_COUPLE':
            self.load_couples(contest_id)


    def load(self):
        
        self.load_contests()
        self.load_signups()
        self.load_description()

        for contest_id in self.contests:
           self.load_contest(contest_id)
       

    def load_description(self):
        
        if self._id == None:
            return
            
        response = requests.get(EVENTPAGE_URL_TEMPLATE.format(language='en', contest=self._id))
        if response.status_code != 200:
            return

        eventpage = BeautifulSoup(response.text, 'html5lib')
        titles = eventpage.find_all('title')
        if titles:
            self._description = titles.text


if __name__ == "__main__":
    pass


