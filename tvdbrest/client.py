# -*- coding: utf-8 -*-
import logging
from functools import wraps
from urllib.parse import urljoin, urlencode

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


def single_response(response_class):
    
    def _inner(func):
        
        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            result = func(obj, *args, **kwargs)
            return response_class(result["data"], obj)
        
        return wrapper
    
    return _inner


def multi_response(response_class):
    def _inner(func):
        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            result = func(obj, *args, **kwargs)
            return [response_class(d, obj) for d in result["data"]]
        
        return wrapper
    
    return _inner


def paged_response(response_class, page_size=100):
    def _inner(func):
        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            result = func(obj, *args, **kwargs)
            return PaginatedAPIObjectList(result['links'],
                                          [response_class(d, obj) for d in result['data']],
                                          multi_response(response_class)(func), tuple([obj] + list(args)), kwargs,
                                          page_size=page_size)
        
        return wrapper
    
    return _inner


class TVDB(object):
    
    def __init__(self, username, userkey, apikey, language=None):
        self.username = username
        self.userkey = userkey
        self.apikey = apikey
        self.accept_language = language or "en"
        
        assert self.username and self.userkey and self.apikey
        self.jwttoken = None
        
        self.useragent = "tvdb-rest %s" % VERSION
        self._series_search_params = None

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
    
    @property
    @login_required
    def series_search_params(self):
        if self._series_search_params is None:
            self._series_search_params = self._api_request('get', '/search/series/params')['data']['params']
        return self._series_search_params

    @multi_response(Language)
    @login_required
    def languages(self):
        return self._api_request('get', '/languages')
    
    @login_required
    def language(self, id):
        return Language(self._api_request('get', '/languages/%s' % id), self)
    
    @single_response(Series)
    @login_required
    def series(self, id):
        return self._api_request('get', '/series/%s' % id)
    
    @multi_response(Series)
    @login_required
    def search(self, **kwargs):
        if not kwargs:
            return {
                "data": []
            }
        u = "/search/series?%s" % urlencode(kwargs)
            
        return self._api_request('get', u)
    
    @multi_response(Actor)
    @login_required
    def actors_by_series(self, id):
        return self._api_request('get', '/series/%s/actors' % id)
    
    @paged_response(Episode)
    @login_required
    def episodes_by_series(self, id, *args, **kwargs):
        u = '/series/%s/episodes' % id
        if kwargs:
            u += "?%s" % urlencode(kwargs)
        
        return self._api_request('get', u)

    @single_response(Episode)
    @login_required
    def episode_details(self, id):
        return self._api_request('get', '/episodes/%s' % id)
    
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
