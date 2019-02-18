import os
import pytest
import re
from MESAeveryday import bcrypt, models
from flask_login import login_user
from datetime import datetime

# use this to login an account
def login_account(client):
    username = "natsu"
    pwd = "a@123456"

    with client:
        response = client.post('/login', data=dict(username=username, password=pwd, submit="Login"), follow_redirects=True)
    return response

# check responsed HTML code
def write_response(filename, response):
    t = open(filename, 'w')
    t.write(str(response.data))
    t.close

# this passed -> login functional!
def test_login(test_client):
    response = login_account(test_client)

    # CHECK response html to make sure it gets redirected to dashboard
    # write_response("login.txt", response)
    assert response.status_code == 200

# @pytest.mark.skip(reason='not now')
def test_level_adding(test_client):
    login_account(test_client)

    # predesigned test data
    data = {
        'College Knowledge -stamps': 1,
        'College Knowledge -submit': 'earn stamp',
        'College Knowledge -time_finished': '02/20/2019'
    }
    data2 = {
        'College Knowledge -stamps': 2,
        'College Knowledge -submit': 'earn stamp',
        'College Knowledge -time_finished': '02/20/2019'
    }
    data3 = {
        'College Knowledge -stamps': 3,
        'College Knowledge -submit': 'earn stamp',
        'College Knowledge -time_finished': '02/20/2019'
    }

    with test_client:
        
        # add 5 pts to the account
        test_client.post('/earn_stamps', data=data, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges/1', follow_redirects=True)

        # badge level should not increase if not adding enough stamps. (here level == 0)
        assert b"<strong> Level <a style=\"font-size: 150%\">0</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>5 points</strong>" in response.data               # 5 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>2 points</strong></a></p>" in response.data    # 2 pts to next level
        
        # add 3 pts to the account
        test_client.post('/earn_stamps', data=data2, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges/1', follow_redirects=True)

        # badge level should increase after adding enough stamps. (here level == 1)
        assert b"<strong> Level <a style=\"font-size: 150%\">1</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>8 points</strong>" in response.data               # 8 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>4 points</strong></a></p>" in response.data    # 4 pts to next level

        # add 3 pts to the account
        test_client.post('/earn_stamps', data=data3, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        response = test_client.get('/badges/1', follow_redirects=True)

        # badge level should not increase to 2 if not adding enough stamps. (here level == 1)
        assert b"<strong> Level <a style=\"font-size: 150%\">1</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>11 points</strong>" in response.data              # 11 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>1 points</strong></a></p>" in response.data    # 1 pts to next level

# @pytest.mark.skip(reason="not now")
def test_level_deleting(test_client):
    login_account(test_client)

    response = test_client.get('/badges/1', follow_redirects=True)
    m = re.findall(b'(<button type="button" class="btn btn btn-danger btn-sm" data-toggle="modal" data-target="#deleteModal" onclick="Values\( \\\')(.+)(\\\', \\\')(.+)(\\\', \\\')(.+)(\\\'\)">)', response.data)

    data = []
    for r in m:
        temp = {
            'stamp_id': r[1].decode("utf-8"),
            'time_finished': r[3].decode("utf-8"),
            'log_date': r[5].decode("utf-8")
        }
        data.append(temp)

    with test_client:
        response = test_client.post('/badges/1', data=data[2], content_type='application/x-www-form-urlencoded', follow_redirects=True)
        
        # badge level should not decrease to 0 if not deleting enough stamps. (here level == 1)
        assert b"<strong> Level <a style=\"font-size: 150%\">1</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>8 points</strong>" in response.data               # 8 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>4 points</strong></a></p>" in response.data    # 4 pts to next level

        response = test_client.post('/badges/1', data=data[1], content_type='application/x-www-form-urlencoded', follow_redirects=True)
        
        # badge level should decrease after deleting enough stamps. (here level == 0)
        assert b"<strong> Level <a style=\"font-size: 150%\">0</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>5 points</strong>" in response.data               # 5 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>2 points</strong></a></p>" in response.data    # 2 pts to next level

        response = test_client.post('/badges/1', data=data[0], content_type='application/x-www-form-urlencoded', follow_redirects=True)
        
        # badge level should decrease to 0 after deleting more than enough stamps. (here level == 0)
        assert b"<strong> Level <a style=\"font-size: 150%\">0</a>" in response.data
        assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>0 points</strong>" in response.data               # 0 accum. pts
        assert b"<a><strong>Point to next level:</strong></a> <a style=\"font-size: 150%\"><strong>7 points</strong></a></p>" in response.data    # 7 pts to next level

# @pytest.mark.skip(reason='for clean-up only')
def test_clean_up(test_client):
    login_account(test_client)

    response = test_client.get('/badges/1', follow_redirects=True)
    m = re.findall(b'(<button type="button" class="btn btn btn-danger btn-sm" data-toggle="modal" data-target="#deleteModal" onclick="Values\( \\\')(.+)(\\\', \\\')(.+)(\\\', \\\')(.+)(\\\'\)">)', response.data)

    data = []
    for r in m:
        temp = {
            'stamp_id': r[1].decode("utf-8"),
            'time_finished': r[3].decode("utf-8"),
            'log_date': r[5].decode("utf-8")
        }
        data.append(temp)
    
    if data:
        for d in data:
            with test_client:
                response = test_client.post('/badges/1', data=d, content_type='application/x-www-form-urlencoded', follow_redirects=True)
    
    assert b"<strong>Total points earned:</strong></a> <a style=\"font-size: 150%\"><strong>0 points</strong>" in response.data     # make sure there's no stamp left
    
# here's a way to test 4 different badge pages
# but doesn't work here
# @pytest.mark.skip(reason='would be a hard time')
# @pytest.mark.parametrize(('url', 'stamp_id', 'required_pt'), [('/badges/1', 5, 7), ('/badges/2', 21, 3), ('/badges/3', 35, 3), ('/badges/4', 44, 2)])
# def test_level_adding(test_client, url, stamp_id, required_pt):
#     login_account(test_client)
#     earned_date = datetime.strptime('2019-2-14', '%Y-%m-%d').date()

#     if stamp_id == 5:
#         with test_client:
#             # response = test_client.post('/earn_stamps', data=dict(College Knowledge -stamps=stamp_id, submit="earn+stamp", time_finished=earned_date), follow_redirects=True)
#             response = test_client.post('/earn_stamps', data={"College+Knowledge+-stamps": stamp_id, "College+KNowledge+-submit": "earn+stamp", "College+Knowledge+-time_finished": earned_date}, follow_redirects=True)
#         write_response("test.txt", response)

#     # response = test_client.get(url, follow_redirects=True)
#     # write_response(filename, response)

#     assert response.status_code == 200