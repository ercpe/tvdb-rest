# -*- coding: utf-8 -*-
import logging
from functools import wraps
from urllib.parse import urljoin

import requests

from tvdbrest import VERSION

logger = logging.getLogger(__name__)


class Unauthorized(Exception):
    pass


class NotFound(Exception):
    pass


class APIError(Exception):
    pass


class APIObject(object):
    STR_ATTR = None
    
    def __init__(self, attrs, tvdb):
        self._attrs = attrs
        self._tvdb = tvdb
    
    def __getattr__(self, item):
        return self._attrs[item]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __str__(self):
        return self._attrs[self.STR_ATTR] if self.STR_ATTR else super(APIObject, self).__str__()


class Language(APIObject):
    STR_ATTR = 'englishName'


class Actor(APIObject):
    STR_ATTR = 'name'


class Series(APIObject):
    STR_ATTR = 'seriesName'
    
    def actors(self):
        return self._tvdb.actors_by_series(self.id)


def login_required(f):
    @wraps(f)
    def wrapper(obj, *args, **kwargs):
        if not obj.logged_in:
            logger.debug("not logged in")
            obj.login()

        try:
            return f(obj, *args, **kwargs)
        except Unauthorized:
            logger.info("Unauthorized API error - login again")
            obj.login()
            return f(obj, *args, **kwargs)
    
    return wrapper


class TVDB(object):
    
    def __init__(self, username, userkey, apikey):
        self.username = username
        self.userkey = userkey
        self.apikey = apikey
        
        assert self.username and self.userkey and self.apikey
        self.jwttoken = None
        
        self.useragent = "tvdb-rest %s" % VERSION

    def login(self):
        self.jwttoken = None
        response = self._api_request('post', '/login', json={
            'username': self.username,
            'userkey': self.userkey,
            'apikey': self.apikey,
        })
        
        self.jwttoken = response['token']
    
    def logout(self):
        self.jwttoken = None
    
    @property
    def logged_in(self):
        return self.jwttoken is not None
    
    @login_required
    def languages(self):
        return self._api_request('get', '/languages', response_class=Language, many=True)
    
    @login_required
    def language(self, id):
        return self._api_request('get', '/languages/%s' % id, response_class=Language, data_attribute=None)
    
    @login_required
    def series(self, id):
        return self._api_request('get', '/series/%s' % id, response_class=Series)
    
    @login_required
    def actors_by_series(self, id):
        return self._api_request('get', '/series/%s/actors' % id, response_class=Actor, many=True)
    
    def _api_request(self, method, relative_url, response_class=None, many=False, data_attribute="data", **kwargs):

        url = urljoin('https://api.thetvdb.com/', relative_url)

        headers = kwargs.pop('headers', {})
        if self.jwttoken:
            headers['Authorization'] = 'Bearer %s' % self.jwttoken

        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise Unauthorized()
        elif response.status_code == 404:
            raise NotFound()
        elif response.status_code >= 400:
            raise APIError()
        
        logger.info("Response: %s", response)
        if response_class:
            data = response.json()[data_attribute] if data_attribute else response.json()
            if many:
                return [response_class(d, self) for d in data]
            return response_class(data, self)
        
        return response.json()
