"""
Millen's Tests
Builds off Luo's test branch
"""
import os
import pytest
from test_level import login_account, write_response
import re

def test_stamp_adding(test_client):
    login_account(test_client)

    data1 = {
        'College Knowledge-stamps': 1,
        'College Knowledge-submit': 'earn stamp',
        'College Knowledge-time_finished': '02/21/2019'
    }
    data2 = {
        'College Knowledge-stamps': 1,
        'College Knowledge-submit': 'earn stamp',
        'College Knowledge-time_finished': '02/22/2019'
    }
    data3 = {
        'College Knowledge-stamps': 2,
        'College Knowledge-submit': 'earn stamp',
        'College Knowledge-time_finished': '02/22/2019'
    }

    with test_client:

        """
            add "Attend MESA Day" stamp for College Knowledge Badge
            -------------------------PASSED----------------------------
        """
        test_client.post('/earn_stamps', data=data1, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges1', follow_redirects=True)

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
        response = test_client.get('/badges1', follow_redirects=True)

        # stamp name should still exist
        assert b"<td>Attend MESA Day</td>" in response.data
        # stamp date should be added to stamp even if already added
        #assert b"<td>2019-02-22</td>" in response.data

        """
            add "Attend a MESA college tour" stamp for College Knowledge Badge
            -------------------------PASSED----------------------------
        """
        test_client.post('/earn_stamps', data=data3, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges1', follow_redirects=True)

        # stamp name should be added to badge even if not already
        assert b"<td>Attend a MESA college tour</td>" in response.data
        # stamp date should be added to stamp even if already added
        assert b"<td>2019-02-22</td>" in response.data

def test_stamp_removing(test_client):
    login_account(test_client)

    """
        remove "Attend MESA Day" stamp for College Knowledge Badge
        ------------------------FAILED----------------------------
    """
    # obtaining stamp information
    response = test_client.get('/badges1', follow_redirects=True)
    m = re.findall(b'(<button type="button" class="btn btn btn-danger btn-sm" data-toggle="modal" data-target="#deleteModal" onclick="Values\( \\\')(.+)(\\\', \\\')(.+)(\\\', \\\')(.+)(\\\'\)">)', response.data)

    data = []
    # use same decoding algorithm
    for r in m:
        temp = {
            'stamp_id': r[1].decode("utf-8"),
            'time_finished': r[3].decode("utf-8"),
            'log_date': r[5].decode("utf-8")
        }
        data.append(temp)

    with test_client:
        response = test_client.post('/badges1', data=data[0], content_type='application/x-www-form-urlencoded', follow_redirects=True)

        # data1 should be removed
        # data3 should still exist
        assert b"<td>Attend a MESA college tour</td>" in response.data
