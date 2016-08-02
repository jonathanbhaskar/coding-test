import os
import json
import tempfile

import pytest

import gistapi


@pytest.fixture
def client(request):
    #db_fd, gistapi.app.config['DATABASE'] = tempfile.mkstemp()
    gistapi.app.config['TESTING'] = True
    client = gistapi.app.test_client()

    #with gistapi.app.app_context():
    #    gistapi.init_db()

    #def teardown():
    #    os.close(db_fd)
    #    os.unlink(flaskr.app.config['DATABASE'])
    #request.addfinalizer(teardown)

    return client


def test_ping(client):
    """Start with a sanity check."""
    rv = client.get('/ping')
    assert b'pong' in rv.data


def test_search(client):
    """Start with a passing test."""
    post_data = {'username': 'justdionysus', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'justdionysus',
                     'pattern': 'TerbiumLabsChallenge_[0-9]+',
                     'matches': [
                        {
                            'filename': 'gistfile1.txt',
                            'url': 'https://gist.github.com/6b2972aa971dd605f524'
                        }
                      ]
                    }
    assert result_dict == expected_dict


def test_multi_search(client):
    post_data = {'username': 'fabpot', 'pattern': 'hello'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'fabpot',
                     'pattern': 'hello',
                     'matches': [
                        {
                            "filename": "gistfile1.php",
                            "url": "https://gist.github.com/6433461"
                        },
                        {
                            "filename": "gistfile2.yml",
                            "url": "https://gist.github.com/6433461"
                        }
                      ]
                    }
    assert result_dict == expected_dict



def test_invalid_users(client):
    post_data = {'username': 'justdysus', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'invalid user',
                     'username': 'justdysus',
                     'pattern': 'TerbiumLabsChallenge_[0-9]+',
                     'matches': []}
    assert result_dict == expected_dict


def test_invalid_pattern(client):
    post_data = {'username': 'justdionysus', 'pattern': ' '}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'Invalid username, pattern',
                     'username': 'justdionysus',
                     'pattern': ' ',
                     'matches': []}
    assert result_dict == expected_dict


# These test cases take a long time to run. Need to create appropriate
# gists on github to test them out.

# def test_pagination(client):
#     post_data = {'username': 'weierophinney', 'pattern': 'php'}
#     rv = client.post('/api/v1/search',
#                      data=json.dumps(post_data),
#                      headers={'content-type':'application/json'})
#     result_dict = json.loads(rv.data.decode('utf-8'))
#     expected_dict = {'status': 'success',
#                      'username': 'weierophinney',
#                      'pattern': 'php',
#                      'matches': []}
#     assert result_dict == expected_dict


# def test_multifile_gist(client):
#     post_data = {'username': 'mybluedog24', 'pattern': '1'}
#     rv = client.post('/api/v1/search',
#                      data=json.dumps(post_data),
#                      headers={'content-type':'application/json'})
#     result_dict = json.loads(rv.data.decode('utf-8'))
#     expected_dict = {'status': 'more than 300 files in a gist',
#                      'username': 'mybluedog24',
#                      'pattern': '1',
#                      'matches': []}
#     assert result_dict == expected_dict
