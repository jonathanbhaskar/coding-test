# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request
import re


# *The* app object
app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The status code and the dict parsed from the json response from the Github API.
        See the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'.format(
            username=username)
    response = requests.get(gists_url)
    status = ''
    gists = []

    # BONUS: What failures could happen?
    # I return the status with the gist
    if response.status_code == 404:
        status = 'invalid user'

    elif status == 500:
        status = 'github error'

    elif status == 200:
        status = 'success'
        gists = response.json()
        # BONUS: Paging? How does this work for users with tons of gists?
        # For users with more than 30 gists, the URL needs to be paginated.
        i = 2
        while response.json():
            response = requests.get(gists_url + '?page=' + str(i))
            gists += response.json()

    return status, gists


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    username = post_data['username']
    pattern = post_data['pattern']

    result = {}
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = []

    # BONUS: Validate the arguments?
    # I could not find specific rules for usernames. So I'm validating for empty arguments alone
    if not username.strip() or not pattern.strip():
        result['status'] = 'Invalid username, pattern'
        return jsonify(result)

    status, gists = gists_for_user(username)
    result['status'] = status

    if status == 'success':
        for gist in gists:

            # BONUS: What about huge gists?
            # The API documentation says the repo needs to be cloned to GET the content of a file
            # larger than 10mb. But just a GET request to the file URL does work.
            # For gists containing more than 300 files, only the first 300 are accessible.
            if gist['truncated']:
                result['status'] = 'more than 300 files in a gist'

            # BONUS: Can we cache results in a datastore/db?

            # REQUIRED: Fetch each gist and check for the pattern
            # A gist can have multiple files, so looping through files
            for f in gist['files'].itervalues():
                response = requests.get(f['raw_url'])
                text = response.text
                regex = re.compile(r'{}'.format(pattern))
                if regex.search(text) is not None:
                    result['matches'].append(gist['html_url'])
                    break

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
