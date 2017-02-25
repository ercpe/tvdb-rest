# -*- coding: utf-8 -*-
import mock
import pytest

from tvdbrest.client import TVDB, Unauthorized


@pytest.fixture
def tvdb():
    return TVDB("myusername", "myuserkey", "myapikey")


@pytest.fixture
def empty_positive_response():
    m = mock.Mock()
    m.status_code = 200
    m.json = mock.Mock(return_value={"data": []})
    return m


class TestLoginLogout(object):
    
    def test_login_status(self):
        tvdb = TVDB("myusername", "myuserkey", "myapikey")
        assert not tvdb.logged_in

    @mock.patch('tvdbrest.client.requests.request')
    def test_login_status_after_login(self, request_mock):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.json = mock.MagicMock(return_value={
            'token': 'jwttoken'
        })
        
        request_mock.return_value = response_mock
        
        tvdb = TVDB("myusername", "myuserkey", "myapikey")
        tvdb.login()
        
        request_mock.assert_called_with('post', 'https://api.thetvdb.com/login', headers={}, json={
            'username': 'myusername',
            'userkey': 'myuserkey',
            'apikey': 'myapikey'
        })

        assert tvdb.logged_in

    @mock.patch('tvdbrest.client.requests.request')
    def test_failed_login(self, request_method_mock):
        response_mock = mock.MagicMock()
        response_mock.status_code = 401
        request_method_mock.return_value = response_mock
        
        tvdb = TVDB("myusername", "myuserkey", "myapikey")
        with pytest.raises(Unauthorized):
            tvdb.login()
        
        assert not tvdb.logged_in

    def test_logout(self, tvdb):
        tvdb.jwttoken = "abc"
        assert tvdb.logged_in
        tvdb.logout()
        assert tvdb.jwttoken is None
        assert not tvdb.logged_in

    @mock.patch('tvdbrest.client.requests.request')
    def test_decorator_login_before_api_call(self, request_method_mock, tvdb):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.json = mock.MagicMock(return_value={"data": []})

        request_method_mock.return_value = response_mock

        login_mock = mock.MagicMock()
        tvdb.login = login_mock
        tvdb.languages()
        
        assert login_mock.called

    @mock.patch('tvdbrest.client.requests.request')
    def test_authorization_for_api_call(self, request_mock, tvdb, empty_positive_response):
        request_mock.return_value = empty_positive_response
        tvdb.jwttoken = "test"
        tvdb.languages()
    
        request_mock.assert_called_with('get', 'https://api.thetvdb.com/languages', headers={
            'Authorization': 'Bearer test'
        })
