# -*- coding: utf-8 -*-

import mock
import pytest

from tvdbrest.client import TVDB, Unauthorized, NotFound, Language


@pytest.fixture
def tvdb():
    tvdb = TVDB("myusername", "myuserkey", "myapikey")
    tvdb.jwttoken = "test-token"
    return tvdb


def api_response_mock(json):
    m = mock.MagicMock()
    m.status_code = 200
    m.json = mock.Mock(return_value=json)
    return m


def api_response_404_mock():
    m = mock.MagicMock()
    m.status_code = 404
    return m


class TestAPI(object):

    @mock.patch('tvdbrest.client.requests.request')
    def test_languages(self, request_method_mock, tvdb):
        request_method_mock.return_value = api_response_mock({
            "data": [
                {
                    "id": 27,
                    "abbreviation": "zh",
                    "name": "中文",
                    "englishName": "Chinese"
                },
                {
                    "id": 7,
                    "abbreviation": "en",
                    "name": "English",
                    "englishName": "English"
                }
        ]})
        
        languages = tvdb.languages()
        assert languages
        assert all(isinstance(x, Language) for x in languages)

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_language(self, request_method_mock, tvdb):
        request_method_mock.return_value = api_response_mock({
            "id": 27,
            "abbreviation": "zh",
            "name": "中文",
            "englishName": "Chinese"
        })
    
        language = tvdb.language(27)
        assert language
        assert language.id == 27

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_language_does_not_exist(self, request_method_mock, tvdb):
        request_method_mock.return_value = api_response_404_mock()
    
        with pytest.raises(NotFound):
            tvdb.language(42)
