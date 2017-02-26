# -*- coding: utf-8 -*-
import math


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

    def episodes(self):
        return self._tvdb.episodes_by_series(self.id)


class Episode(APIObject):
    STR_ATTR = 'episodeName'


class PaginatedAPIObjectList(list):

    def __init__(self, links, initial_items, fetch_func, fetch_args=None, page_size=100):
        self._first_page = links['first']
        self._last_page = links['last']

        self._pages = [initial_items]
        if self._first_page != self._last_page:
            self._pages.extend([None for _ in range(self._first_page+1, self._last_page+1)])

        self._page_size = page_size
        self._fetch_func = fetch_func
        self._fetch_args = fetch_args
        super(PaginatedAPIObjectList, self).__init__()

    @property
    def _last_page_item_count(self):
        if self._pages[self._last_page-1] is None:
            self._pages[self._last_page-1] = self._fetch_page(self._last_page)
            
        return len(self._pages[self._last_page-1])

    def _fetch_page(self, page_number):
        return self._fetch_func(*tuple(list(self._fetch_args or []) + [page_number]))

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
