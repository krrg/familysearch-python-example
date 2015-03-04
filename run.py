from flask import Flask, render_template, redirect, request, jsonify
import requests

import os.path

app = Flask(__name__)



@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


def get_app_key():
    cd = os.path.dirname(os.path.realpath(__file__))
    with open(cd + os.path.sep + 'appkey.txt', 'r') as f:
        return f.readline().strip()


@app.route('/login')
def login():
    app_key = get_app_key()  # Store this somewhere else

    # Build the URL for making the request
    authorization_url = requests.Request(
        method = 'GET',
        url='https://sandbox.familysearch.org/cis-web/oauth2/v3/authorization',
        params={
            'response_type': 'code',
            'client_id': app_key,
            'redirect_uri': 'http://localhost:8000/return',
        }
    ).prepare().url

    return redirect(authorization_url)


@app.route('/return')
def fs_return():
    auth_code = str(request.args['code'])  # Passed back from FamilySearch
    token_endpoint = 'https://sandbox.familysearch.org/cis-web/oauth2/v3/token'

    r = requests.post(token_endpoint, data={
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': get_app_key()
    }, headers={
        'Accept': 'application/json'
    })

    # TODO: Check to see if status code was 200

    # Store this access token to make future requests in behalf of the user.

    access_token = r.json()['access_token']
    return current_tree_person(access_token)


def current_tree_person(access_token):
    response = requests.get(
        url='https://sandbox.familysearch.org/platform/tree/current-person',
        headers={
            'Authorization': "Bearer " + access_token,
            'Accept': 'application/json',
        }
    )
    json_response = response.json()

    return render_template('person_info.html', display=json_response['persons'][0]['display'])


if __name__ == '__main__':
    app.run(port=8000, debug=True)
