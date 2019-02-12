"""
By Millen
"""
import pytest
import os
from MESAeveryday import bcrypt, models, app
from flask_login import login_user
from datetime import datetime

script_dir = os.path.dirname(__file__)
rel_path = "test_logs/test_remove.txt"
abs_path = os.path.join(script_dir, rel_path)

def test_remove(test_client):

    response = test_client.post('/', data=dict(username="jsmith", password="aaaaaa1!"), follow_redirects=True)
    t = open(abs_path, "a+")
    t.write(str(response.data))
    t.close()

    assert response.status_code == 200