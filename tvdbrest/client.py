# -*- coding: utf-8 -*-
import logging
from functools import wraps
from urllib.parse import urljoin

import requests

from tvdbrest import VERSION
from tvdbrest.objects import *

logger = logging.getLogger(__name__)


class Unauthorized(Exception):
    pass


class NotFound(Exception):
    pass


class APIError(Exception):
    pass


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
    
    def __init__(self, username, userkey, apikey, language=None):
        self.username = username
        self.userkey = userkey
        self.apikey = apikey
        self.accept_language = language or "en"
        
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
        return self._multi_response('get', '/languages', response_class=Language)
    
    @login_required
    def language(self, id):
        return self._single_response('get', '/languages/%s' % id, response_class=Language, data_attribute=None)
    
    @login_required
    def series(self, id):
        return self._single_response('get', '/series/%s' % id, response_class=Series)
    
    @login_required
    def actors_by_series(self, id):
        return self._multi_response('get', '/series/%s/actors' % id, response_class=Actor)
    
    @login_required
    def episodes_by_series(self, id):
        u = '/series/%s/episodes' % id
        
        return self._paged_response('get', u, Episode, self.__episode_page_by_series, (id, ))

    @login_required
    def __episode_page_by_series(self, id, page):
        u = '/series/%s/episodes?page=%s' % (id, page)
        return self._multi_response('get', u, Episode)
    
    def _single_response(self, method, relative_url, response_class, data_attribute="data", **kwargs):
        response_json = self._api_request(method, relative_url, **kwargs)
        data = response_json[data_attribute] if data_attribute else response_json
        return response_class(data, self)

    def _multi_response(self, method, relative_url, response_class, data_attribute="data", **kwargs):
        response_json = self._api_request(method, relative_url, **kwargs)
        data = response_json[data_attribute] if data_attribute else response_json
        return [response_class(d, self) for d in data]
    
    def _paged_response(self, method, relative_url, response_class, fetch_func, fetch_args=None, page_size=100, **kwargs):
        response_json = self._api_request(method, relative_url, **kwargs)
        return PaginatedAPIObjectList(response_json['links'], [
            response_class(d, self) for d in response_json['data']
        ], fetch_func, fetch_args, page_size=page_size)
    
    def _api_request(self, method, relative_url, data_attribute="data", **kwargs):
        url = urljoin('https://api.thetvdb.com/', relative_url)

        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self.useragent
        if self.jwttoken:
            headers['Authorization'] = 'Bearer %s' % self.jwttoken
        if self.accept_language:
            headers['Accept-Language'] = self.accept_language

        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise Unauthorized()
        elif response.status_code == 404:
            raise NotFound()
        elif response.status_code >= 400:
            raise APIError()
        
        logger.info("Response: %s", response)
        return response.json()
