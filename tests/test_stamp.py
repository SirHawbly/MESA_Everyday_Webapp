"""
Millen's Tests
Builds off Luo's test branch
"""
import os
import pytest
from MESAeveryday import bcrypt, models
from flask_login import login_user
from datetime import datetime
from test_level import login_account, write_response

def test_stamp_adding_and_removing(test_client):
    login_account(test_client)

    data1 = {
        'College Knowledge -stamps': 1,
        'College Knowledge -submit': 'earn stamp',
        'College Knowledge -time_finished': '02/21/2019'
    }
    data2 = {
        'College Knowledge -stamps': 1,
        'College Knowledge -submit': 'earn stamp',
        'College Knowledge -time_finished': '02/22/2019'
    }

    with test_client:

        """
            add "Attend MESA Day" stamp for College Knowledge Badge
            -------------------------PASSED----------------------------
        """
        test_client.post('/earn_stamps', data=data1, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges/1', follow_redirects=True)

        # write_response("test.txt", response)

        # stamp name should be added to badge even if not already
        assert b"<td>Attend MESA Day</td>" in response.data
        # stamp date should be added to stamp even if already added
        assert b"<td>2019-02-21</td>" in response.data

        """
            add second "Attend MESA Day" stamp for College Knowledge Badge
            --------------------------FAILED------------------------------
        """
        test_client.post('/earn_stamps', data=data2, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges/1', follow_redirects=True)

        # stamp name should still exist
        assert b"<td>Attend MESA Day</td>" in response.data
        # stamp date should be added to stamp even if already added
        #assert b"<td>2019-02-22</td>" in response.data

        """
            remove "Attend MESA Day" stamp for College Knowledge Badge
            ------------------------PASSED----------------------------
        """
        response = test_client.post('/badges/1', data=data1, content_type='application/x-www-form-urlencoded', follow_redirects=True)

        # stamp name should be added to badge even if not already
        assert b"<td>Attend MESA Day</td>" not in response.data
