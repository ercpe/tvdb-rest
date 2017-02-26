# -*- coding: utf-8 -*-
import datetime

import mock
import pytest

from tvdbrest.objects import PaginatedAPIObjectList, Language, Series


class TestAPIObject(object):
    
    def test_eq(self):
        lang = Language({'id': 1}, None)
        lang2 = Language({'id': 1}, None)
        
        assert lang == lang2
        
        series = Series({'id': 1}, None)
        assert lang != series

    def test_str(self):
        lang = Language({'id': 1, 'englishName': 'Dummy'}, None)
        assert str(lang) == "Dummy"


class TestSeriesObject(object):
    
    def test_first_aired(self):
        s = Series({}, None)
        assert s.firstAired is None
        
        s = Series({
            'firstAired': "1989-12-17"
        }, None)
        
        assert s.firstAired is not None
        assert isinstance(s.firstAired, datetime.date)
        assert s.firstAired == datetime.date(1989, 12, 17)

    def test_last_updated(self):
        s = Series({}, None)
        assert s.lastUpdated is None
        
        s = Series({
            'lastUpdated': 1
        }, None)
        assert s.lastUpdated is not None
        assert isinstance(s.lastUpdated, datetime.datetime)
        assert s.lastUpdated == datetime.datetime(1970, 1, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        

class TestPagination(object):

    def test_slicing(self):
        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 7,
            "next": 2,
            "prev": None
        }, [], None, page_size=1)

        with pytest.raises(ValueError):
            paol[1:2]

    def test_indexing_out_of_bounds(self):
        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 5,
            "next": 2,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], None, page_size=5)

        # beyond of page_size * number of pages - definitely out of bounds
        with pytest.raises(IndexError):
            paol[25]
        
        # absolute item index below 0
        with pytest.raises(IndexError):
            paol[-30]

    def test_indexing_out_of_bounds_multiple_pages(self):
        fetch_mock = mock.Mock(return_value=[6,7,8])

        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 2,
            "next": 2,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], fetch_mock, page_size=5)

        with pytest.raises(IndexError):
            paol[9]

        fetch_mock.assert_called_once_with(2)

    def test_indexing(self):
        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 1,
            "next": None,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], None, page_size=5)
    
        for i in range(0, 5):
            x = paol[i]
            assert x == (i+1)

    def test_indexing_fetching(self):
        fetch_mock = mock.Mock(return_value=[6, 7, 8])

        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 2,
            "next": None,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], fetch_mock, page_size=5)

        for i in 0, 1, 2, 3, 4, 5, 6, 7:
            x = paol[i]
            assert x == i + 1

        fetch_mock.assert_called_once_with(2)

    def test_indexing_fetching2(self):
        def _dummy_fetch(page):
            if page == 2:
                return [6, 7, 8, 9, 10]
            elif page == 3:
                return [11, 12]

        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 3,
            "next": None,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], _dummy_fetch, page_size=5)

        for i in 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11:
            x = paol[i]
            assert x == i + 1

        with pytest.raises(IndexError):
            paol[12]

    def test_len(self):
        def _dummy_fetch(page):
            if page == 2:
                return [6, 7, 8, 9, 10]
            elif page == 3:
                return [11, 12]

        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 3,
            "next": None,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], _dummy_fetch, page_size=5)

        assert len(paol) == 12

    def test_iter(self):
        def _dummy_fetch(page):
            if page == 2:
                return [6, 7, 8, 9, 10]
            elif page == 3:
                return [11, 12]

        paol = PaginatedAPIObjectList({
            "first": 1,
            "last": 3,
            "next": None,
            "prev": None
        }, [
            1, 2, 3, 4, 5
        ], _dummy_fetch, page_size=5)

        assert len(paol) == 12

        assert list(paol) == [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
        ]

        for i, item in enumerate(paol, 1):
            assert item == i
