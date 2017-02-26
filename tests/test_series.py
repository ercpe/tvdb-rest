# -*- coding: utf-8 -*-

import mock
import pytest

from tests.base import TestBase, tvdb
from tvdbrest.client import NotFound, Series


class TestSeriesAPI(TestBase):

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_series(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            "data": {
                "id": 1,
            }
        })

        series = tvdb.series(1)
        assert series
        assert isinstance(series, Series)
        assert series.id == 1
    
    def test_get_series_without_fields(self, tvdb):
        tvdb._api_request = mock.MagicMock()
        tvdb.series(123)
        tvdb._api_request.assert_called_with('get', '/series/123')

    def test_get_series_with_single_field(self, tvdb):
        tvdb._api_request = mock.MagicMock()
        tvdb.series(123, keys=['foo'])
        tvdb._api_request.assert_called_with('get', '/series/123/filter?keys=foo')

    def test_get_series_with_fields(self, tvdb):
        tvdb._api_request = mock.MagicMock()
        tvdb.series(123, keys=['foo', 'bar', 'baz'])
        tvdb._api_request.assert_called_with('get', '/series/123/filter?keys=foo%2Cbar%2Cbaz')

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_series_does_not_exist(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_404_mock()
        
        with pytest.raises(NotFound):
            tvdb.series(42)

    def test_episode_by_series(self, tvdb):
        tvdb._api_request = mock.MagicMock()
        
        s = Series({'id': 123}, tvdb)
        s.episodes()

        tvdb._api_request.assert_called_with('get', '/series/123/episodes')

    def test_episode_by_series_with_query(self, tvdb):
        tvdb._api_request = mock.MagicMock()
    
        s = Series({'id': 123}, tvdb)
        s.episodes(airedSeason=2)

        tvdb._api_request.assert_called_with('get', '/series/123/episodes/query?airedSeason=2')

    def test_get_series_keys_params(self, tvdb):
        tvdb._api_request = mock.MagicMock()
        
        tvdb.series_key_params(123)
        tvdb._api_request.assert_called_with('get', '/series/123/filter/params')
