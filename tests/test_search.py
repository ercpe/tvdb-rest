# -*- coding: utf-8 -*-

import mock
import pytest

from tests.base import TestBase, tvdb
from tvdbrest.client import NotFound


class TestSearchAPI(TestBase):

    @mock.patch('tvdbrest.client.requests.request')
    def test_series_search_params(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            "data": {
                "params": ["foo", "bar", "baz"],
            }
        })
        
        assert tvdb.series_search_params == ["foo", "bar", "baz"]
        request_method_mock.assert_called_once()

    @mock.patch('tvdbrest.client.requests.request')
    def test_series_search_no_args(self, request_method_mock, tvdb):
        assert tvdb.search() == []
        request_method_mock.assert_not_called()
    
    @mock.patch('tvdbrest.client.requests.request')
    def test_series_search(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            'data': [{
                'id': 1,
                'seriesName': 'Dummy'
            }]
        })
        
        search_result = tvdb.search(name='foo')
        assert search_result
        assert search_result[0].id == 1

    @mock.patch('tvdbrest.client.requests.request')
    def test_series_search_not_found(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_404_mock()

        with pytest.raises(NotFound):
            tvdb.search(name='foo')
