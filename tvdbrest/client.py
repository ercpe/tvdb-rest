# -*- coding: utf-8 -*-
import logging
from functools import wraps
from urllib.parse import urljoin, urlencode

import requests

from tvdbrest import VERSION
from tvdbrest.objects import *
import datetime
import time

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
    def language(self, language_id):
        return Language(self._api_request('get', '/languages/%s' % language_id), self)
    
    @single_response(Series)
    @login_required
    def series(self, series_id, keys=None):
        u = '/series/%s' % series_id
        if keys:
            u += "/filter?%s" % urlencode({
                'keys': ','.join(keys)
            })
        return self._api_request('get', u)
    
    @login_required
    def series_key_params(self, series_id):
        return self._api_request('get', '/series/%s/filter/params' % series_id)['data']['params']
    
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
    def actors_by_series(self, series_id):
        return self._api_request('get', '/series/%s/actors' % series_id)
    
    @paged_response(Episode)
    @login_required
    def episodes_by_series(self, series_id, *args, **kwargs):
        u = '/series/%s/episodes' % series_id
        if kwargs:
            if not (len(kwargs) == 1 and 'page' in kwargs):
                u += '/query'
            u += "?%s" % urlencode(kwargs)
        
        return self._api_request('get', u)

    @login_required
    def episode_query_params(self, series_id):
        return self._api_request('get', '/series/%s/episodes/query/params' % series_id)['data']

    @single_response(Episode)
    @login_required
    def episode_details(self, episode_id):
        return self._api_request('get', '/episodes/%s' % episode_id)
    
    @single_response(ImageCount)
    @login_required
    def image_count(self, series_id):
        return self._api_request('get', '/series/%s/images' % series_id)
    
    @multi_response(Image)
    @login_required
    def images(self, series_id, **kwargs):
        u = '/series/%s/images/query' % series_id
        if kwargs:
            u += "?%s" % urlencode(kwargs)
        return self._api_request('get', u)
    
    @multi_response(Update)
    @login_required
    def updates(self, from_time, to_time=None):
        u = '/updated/query?'
        
        def _dt_to_epoch(o):
            return int(time.mktime(o.timetuple())) - time.timezone if isinstance(o, datetime.datetime) else o
        
        kwargs = {
            'fromTime': _dt_to_epoch(from_time)
        }
        if to_time:
            kwargs['toTime'] = _dt_to_epoch(to_time)
        
        u += urlencode(kwargs)
        return self._api_request('get', u)
    
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
            raise Unauthorized(response.json()["Error"])
        elif response.status_code == 404:
            raise NotFound(response.json()["Error"])
        elif response.status_code >= 400:
            raise APIError()
        
        logger.info("Response: %s", response)
        return response.json()
