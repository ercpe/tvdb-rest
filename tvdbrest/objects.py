# -*- coding: utf-8 -*-
import datetime
import math


class LastUpdatedFieldMixin(object):

    @property
    def lastUpdated(self):  # NOSONAR
        lu = self._attrs.get('lastUpdated', None)
        if not lu:
            return None
        
        return datetime.datetime.fromtimestamp(lu, tz=datetime.timezone.utc)


class FirstAiredFieldMixin(object):

    @property
    def firstAired(self):  # NOSONAR
        s = self._attrs.get('firstAired', None)
        if not s:
            return None
        
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()


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


class Series(LastUpdatedFieldMixin, FirstAiredFieldMixin, APIObject):
    STR_ATTR = 'seriesName'
    
    def actors(self):
        return self._tvdb.actors_by_series(self.id)

    def episodes(self, **kwargs):
        return self._tvdb.episodes_by_series(self.id, **kwargs)

    def images(self, **kwargs):
        return self._tvdb.images(self.id, **kwargs)


class Episode(LastUpdatedFieldMixin, FirstAiredFieldMixin, APIObject):
    STR_ATTR = 'episodeName'


class ImageCount(APIObject):
    pass


class Image(APIObject):

    @property
    def url(self):
        return "http://thetvdb.com/banners/%s" % self.fileName

    @property
    def thumbnail_url(self):
        return "http://thetvdb.com/banners/%s" % self.thumbnail


class Update(LastUpdatedFieldMixin, APIObject):
    
    @property
    def series(self):
        return self._tvdb.series(self.id)


class PaginatedAPIObjectList(list):

    def __init__(self, links, initial_items, fetch_func, fetch_args=None, fetch_kwargs=None, page_size=100):
        self._first_page = links['first']
        self._last_page = links['last']

        self._pages = [initial_items]
        if self._first_page != self._last_page:
            self._pages.extend([None for _ in range(self._first_page+1, self._last_page+1)])

        self._page_size = page_size
        self._fetch_func = fetch_func
        self._fetch_args = fetch_args
        self._fetch_kwargs = fetch_kwargs
        super(PaginatedAPIObjectList, self).__init__()

    @property
    def _last_page_item_count(self):
        if self._pages[self._last_page-1] is None:
            self._pages[self._last_page-1] = self._fetch_page(self._last_page)
            
        return len(self._pages[self._last_page-1])

    def _fetch_page(self, page_number):
        kwargs = self._fetch_kwargs or {}
        kwargs['page'] = page_number
        return self._fetch_func(*self._fetch_args or (), **kwargs)

    def __len__(self):
        return (self._last_page-1) * self._page_size + self._last_page_item_count

    def __iter__(self):
        def _iter_pages():
            for page_idx in range(self._first_page-1, self._last_page):
                if self._pages[page_idx] is None:
                    self._pages[page_idx] = self._fetch_page(page_idx+1)
                for page_item in self._pages[page_idx]:
                    yield page_item
                    
        return iter(_iter_pages())

    def __getitem__(self, item):
        if isinstance(item, slice):
            raise ValueError("slicing not supported")
        
        if item >= 0:
            absolute_index = item
        else:
            # item from the end of the list
            absolute_index = (self._last_page * self._page_size)-1 - item
        
        # definitely out of bounds
        if not 0 <= absolute_index <= (self._last_page * self._page_size)-1:
            raise IndexError("list index out of range")

        # test if we have fetched the page the item belongs to
        page_idx = int(math.floor(absolute_index / (self._page_size * 1.0)))
        page_item_idx = absolute_index - (page_idx * self._page_size)

        if self._pages[page_idx] is None:
            self._pages[page_idx] = self._fetch_page(page_idx+1)

        # if we've already fetched the last page, we can determine for sure that the index is out of range
        if absolute_index >= 0 and self._pages[self._last_page-1] is not None and \
            page_item_idx >= len(self._pages[self._last_page-1]):
                raise IndexError("list index out of range")

        return self._pages[page_idx][page_item_idx]
