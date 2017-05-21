"""Defines oauth endpoints"""

import os
import httplib2
import requests
import json
from flask import Blueprint, make_response, request, session
from flask import flash, redirect, url_for
from .. infrastructure import helper_methods
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

oauth_page = Blueprint('oauth_page', __name__,
                       template_folder='templates')

# Get current working directory
client_secret_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'views/oauth')


@oauth_page.route('/gconnect', methods=['POST'])
def gconnect():
    '''Authenticate user from google plus and set in session'''
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            os.path.join(client_secret_path,
                         'google_client_id.json'), scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    client_id = json.loads(open(
        os.path.join(client_secret_path,
                     'google_client_id.json'), 'r').read())[
        'web']['client_id']

    # Verify that the access token is used for this app.
    if result['issued_to'] != client_id:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            "Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in session for later use
    session['provider'] = 'google'
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    session['username'] = data["name"]
    session['picture'] = data["picture"]
    session['email'] = data["email"]

    # Log in the user
    uid = helper_methods.getUserId(session['email'])
    if not uid:
        uid = helper_methods.createUser()
    session['user_id'] = uid

    output = ''
    output += 'Welcome, ' + session['username']
    output += '<img src ="' + session['picture']
    output += '" height=300px width=300px style ="img-responsive">'
    flash("You are now logged in as %s" % session['username'])
    return output


@oauth_page.route('/gdisconnect')
def gdisconnect():
    '''Disconnect user from google plus'''
    # Only disconnect a connected user
    access_token = session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Revoke HTTP get request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # The given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@oauth_page.route('/fbconnect', methods=["POST"])
def fbconnect():
    '''Authenticate user from facebook and set in session'''
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Exchange client token for long lived server side token with GET/
    # oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={client-secret}&fb_exchange_token={short-lived-token}
    client_secret = json.loads(
        open(
            os.path.join(client_secret_path,
                         'fb_client_secret.json'), 'r').read())['web']
    app_id = client_secret['app_id']
    app_secret = client_secret['app_secret']
    url = 'https://graph.facebook.com/v2.9/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    token = json.loads(content)

    # use token to get user info from api
    userinfo_url = "https://graph.facebook.com/oauth2/me"

    url = 'https://graph.facebook.com/v2.9/me?fields=id,email,name,picture&access_token=%s' % token.get(
        'access_token')

    # Create an http request
    h = httplib2.Http()

    # Get the response and content from url
    response, content = h.request(url, 'GET')

    data = json.loads(content)
    if 'error' in data:
        response = make_response(json.dumps(
            'Error occurred while getting user data from facebook'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Set login details in session
    session['provider'] = 'facebook'
    session['username'] = data['name']
    session['email'] = data['email']
    session['facebook_id'] = data['id']
    session['picture'] = data['picture']['data']['url']

    # See if user exists
    user_id = helper_methods.getUserId(session['email'])
    if not user_id:
        user_id = helper_methods.createUser()
    session['user_id'] = user_id

    output = ''
    output += 'Welcome, ' + session['username']
    output += '<img src ="'
    output += session['picture']
    output += '" width=300px height=300px style ="img-responsive">'
    flash("You are now logged in as %s" % session['username'])
    return output


@oauth_page.route('/fbdisconnect')
def fbdisconnect():
    '''Disconnect user from facebook on logout'''
    facebook_id = session.get('facebook_id')
    access_token = session.get('access_token')
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out'


@oauth_page.route('/gitconnect')
def gitConnect():
    '''Authenticate user from github and set in session'''
    if request.args.get("state") != session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get the code from request
    code = request.args.get("code")

    # Load the client id and client secret
    github_secret = json.loads(
        open(
            os.path.join(client_secret_path,
                         'github_client_secret.json'), 'r').read())['web']
    client_id = github_secret['client_id']
    client_secret = github_secret['client_secret']
    redirect_uri = "http://localhost:8000"
    url = 'https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s&redirect_uri=%s' % (
        client_id, client_secret, code, redirect_uri)
    h = httplib2.Http()
    response, content = h.request(url, 'POST')
    token = content and content.split("&")[0].strip()
    url = "https://api.github.com/user?access_token=%s" % token.split("=")[1]

    # Create an http request
    h = httplib2.Http()

    # Get response and content from the request
    response, content = h.request(url, 'GET')

    data = json.loads(content)
    if 'error' in data:
        response = make_response(json.dumps(
            'Error occurred while getting user data from facebook'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Set login details in session
    session['provider'] = 'github'
    session['username'] = data['login']
    session['email'] = data['email']
    session['github_id'] = data['id']
    session['picture'] = data['avatar_url']

    # See if user exists
    user_id = helper_methods.getUserId(session['email'])
    if not user_id:
        user_id = helper_methods.createUser()
    session['user_id'] = user_id
    flash("You are now logged in as %s" % session['username'])
    return redirect(url_for('home_page.home'))


@oauth_page.route('/logout')
def logout():
    if 'provider' in session:
        if session['provider'] == 'google':
            gdisconnect()
            del session['gplus_id']
            del session['access_token']
        if session['provider'] == 'facebook':
            fbdisconnect()
            del session['facebook_id']
        if session['provider'] == 'github':
            del session['github_id']

        del session['username']
        del session['email']
        del session['picture']
        del session['user_id']
        del session['provider']
        flash('You have been logged out')
        return redirect(url_for('home_page.home'))
    else:
        flash('You were not logged in to begin with')
        return redirect(url_for('home_page.home'))
