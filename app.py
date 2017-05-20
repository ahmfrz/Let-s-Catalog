import random
import string
import json
import httplib2
import requests
from flask import Flask, make_response, render_template, jsonify, request
from flask import redirect, url_for, session, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Product, Product_Pics, Product_Specs
from database_setup import Category, Brand, SubCategory, User
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

# Create connection with the database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

make_session = sessionmaker(bind=engine)
dbsession = make_session()

# region decorators


def user_loggedin(function):
    """Decorator to check if user is logged in"""
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return function(*args, **kwargs)
        else:
            flash('You must be logged in to access this page')
            session['last_URL'] = request.url
            return redirect(url_for('home'))
    return decorated_function


def db_add_commit(entity):
    dbsession.add(entity)
    dbsession.commit()


def db_delete_commit(entity):
    dbsession.delete(entity)
    dbsession.commit()


def checkIfCategoryExists(categoryName):
    return dbsession.query(Category).filter_by(name=categoryName).first()


def checkIfSubCategoryExists(category_id, subcategoryName):
    return dbsession.query(SubCategory).filter_by(
        name=subcategoryName,
        category_id=category_id).first()


def checkIfProductExists(subcategory_id, productName):
    return dbsession.query(Product).filter_by(
        name=productName,
        subcategory_id=subcategory_id).first()

# Adding new users


def createUser():
    newUser = User(name=session['username'], email=session['email'],
                   picture=session['picture'])
    dbsession.add(newUser)
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = dbsession.query(User).filter_by(id=user_id).first()
    return user


def getUserId(email):
    user = dbsession.query(User).filter_by(email=email).first()
    return user and user.id


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_id.json', scope='')
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

    client_id = json.loads(open('google_client_id.json', 'r').read())['web']['client_id']

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
    uid = getUserId(session['email'])
    if not uid:
        uid = createUser()
    session['user_id'] = uid

    output = ''
    output += 'Welcome, ' + session['username']
    output += '<img src ="' + session['picture']
    output += '" height=300px width=300px style ="img-responsive">'
    flash("You are now logged in as %s" % session['username'])
    return output

# Disconnect Revoke current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
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

# Facebook login


@app.route('/fbconnect', methods=["POST"])
def fbconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Exchange client token for long lived server side token with GET/
    # oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={client-secret}&fb_exchange_token={short-lived-token}
    client_secret = json.loads(open('fb_client_secret.json', 'r').read())['web']
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
    h = httplib2.Http()
    response, content = h.request(url, 'GET')

    data = json.loads(content)
    if 'error' in data:
        response = make_response(json.dumps(
            'Error occurred while getting user data from facebook'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    session['provider'] = 'facebook'
    session['username'] = data['name']
    session['email'] = data['email']
    session['facebook_id'] = data['id']
    session['picture'] = data['picture']['data']['url']

    # See if user exists
    user_id = getUserId(session['email'])
    if not user_id:
        user_id = createUser()
    session['user_id'] = user_id

    output = ''
    output += 'Welcome, ' + session['username']
    output += '<img src ="'
    output += session['picture']
    output += '" width=300px height=300px style ="img-responsive">'
    flash("You are now logged in as %s" % session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = session.get('facebook_id')
    access_token = session.get('access_token')
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out'


@app.route('/gitconnect')
def gitConnect():
    if request.args.get("state") != session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.args.get("code")
    github_secret = json.loads(open('github_client_secret.json', 'r').read())['web']
    client_id = github_secret['client_id']
    client_secret = github_secret['client_secret']
    redirect_uri = "http://localhost:8000"
    url = 'https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s&redirect_uri=%s' % (
        client_id, client_secret, code, redirect_uri)
    h = httplib2.Http()
    response, content = h.request(url, 'POST')
    token = content and content.split("&")[0].strip()
    url = "https://api.github.com/user?access_token=%s" % token.split("=")[1]
    h = httplib2.Http()
    response, content = h.request(url, 'GET')

    data = json.loads(content)
    if 'error' in data:
        response = make_response(json.dumps(
            'Error occurred while getting user data from facebook'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    session['provider'] = 'github'
    session['username'] = data['login']
    session['email'] = data['email']
    session['github_id'] = data['id']
    session['picture'] = data['avatar_url']

    # See if user exists
    user_id = getUserId(session['email'])
    if not user_id:
        user_id = createUser()
    session['user_id'] = user_id
    flash("You are now logged in as %s" % session['username'])
    return redirect(url_for('home'))


@app.route('/gitdisconnect')
def gitdisconnect():
    github_id = session.get('github_id')
    access_token = session.get('access_token')
    return 'You have been logged out'


@app.route('/logout')
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
        flash('You have been logged out')
        return redirect(url_for('home'))
    else:
        flash('You were not logged in to begin with')
        return redirect(url_for('home'))


@app.route('/index')
@app.route('/')
def home():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    if 'username' in session and 'last_URL' in session:
        url = session['last_URL']
        del session['last_URL']
        return redirect(url)
    items = dbsession.query(Category, SubCategory, Product, Product_Pics).join(
        SubCategory, Product, Product_Pics).order_by(
        Category.created_date).limit(5).all()
    return render_template('home.html', items=items, count=len(items),
                           STATE=session['state'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for(session['last_URL']))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template('login.html', STATE=state)

# CRUD operations for category


@app.route('/catalog/<category_param>/')
def showCategory(category_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategories = dbsession.query(SubCategory).filter_by(
            category_id=category.id).all()
        return render_template('showCategory.html', category=category,
                               subcategories=subcategories)
    else:
        flash('Category not found')
        return redirect(url_for('home'))


@app.route('/catalog/user_categories')
@user_loggedin
def showUserCategory():
    category = dbsession.query(Category).filter_by(
        user_id=session['user_id']).all()
    return render_template('showAllCategories.html', categories=category)
    if category:
        subcategories = dbsession.query(SubCategory).filter_by(
            category_id=category.id).all()
        return render_template('showCategory.html', category=category,
                               subcategories=subcategories)
    else:
        flash('You have not created any categories')
        return redirect(url_for('home'))


@app.route('/catalog/category/add', methods=['GET', 'POST'])
@user_loggedin
def addCategory():
    if request.method == 'POST':
        categoryName = request.form.get("cat_name")
        if categoryName:
            if not checkIfCategoryExists(categoryName):
                newCategory = Category(
                    name=categoryName, user_id=session['user_id'])
                db_add_commit(newCategory)
                flash('New category added: %s' % newCategory.name)
                return redirect(url_for('home'))
            else:
                flash('Category already exists')
                return redirect(url_for('addCategory'))
        else:
            flash('Category name must not be empty')
            return redirect(url_for('addCategory'))
    else:
        return render_template('addCategory.html')


@app.route('/catalog/category/delete/<int:category_id>',
           methods=['GET', 'POST'])
@user_loggedin
def deleteCategory(category_id):
    category = dbsession.query(Category).filter_by(id=category_id).first()
    if not category:
        flash('Category not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = category.name
        db_delete_commit(category)
        flash('Category deleted: %s' % name)
        return redirect(url_for('home'))
    else:
        return render_template('confirmDelete.html', item=category.name)


@app.route('/catalog/category/edit/<int:category_id>', methods=['GET', 'POST'])
@user_loggedin
def editCategory(category_id):
    category = dbsession.query(Category).filter_by(id=category_id).first()
    if not category:
        flash('Category not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('cat_Name')
        if name:
            category.name = name
            flash('Category updated %s' % category.name)
            return redirect(url_for('home'))
        else:
            flash('Category name must not be empty')
            return redirect(url_for('editCategory', category_id=category_id))
    else:
        return render_template('editCategory.html', category=category)

# CRUD operations for sub category


@app.route('/catalog/<category_param>/<subcategory_param>')
def showSubCategory(category_param, subcategory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()
        if subcategory:
            products = dbsession.query(Product).filter_by(
                subcategory_id=subcategory.id).all()
            return render_template('showSubCategory.html', category=category,
                                   subcategory=subcategory, products=products)
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))


@app.route('/catalog/<category_param>/<subcategory_param>/brands')
def showSubCategoryBrand(category_param, subcategory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()
        if subcategory:
            brands = dbsession.query(Brand).filter_by(
                subcategory_id=subcategory.id).all()
            return render_template('showBrand.html', category=category,
                                   subcategory=subcategory, brands=brands)
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))


@app.route('/catalog/<category_param>/subcategory/add',
           methods=['GET', 'POST'])
@user_loggedin
def addSubCategory(category_param):
    categories = dbsession.query(Category).all()
    category = None
    # Get category from the passed parameter
    for item in categories:
        if item.name == category_param:
            category = item
            break

    # Don't proceed if the category is invalid
    if not category:
        flash('Invalid category')
        return redirect(url_for('home'))
    else:
        if(request.method == 'POST'):
            subcategory_Name = request.form.get('sub_Name')
            subcategory_Desc = request.form.get('sub_Description')
            category_name = request.form.get('cat_name')
            category_name = category_name and category_name.replace("+", " ")

            # Check if the user has entered name and description
            if subcategory_Name and subcategory_Desc and category_name:
                if category_name != category_param:
                    category = filter(lambda cat: cat.name ==
                                      category_name, categories)[0]
                if not checkIfSubCategoryExists(category.id, subcategory_Name):
                    subcategory = SubCategory(
                        name=subcategory_Name, description=subcategory_Desc,
                        category_id=category.id, user_id=session['user_id'])
                    db_add_commit(subcategory)
                    flash('Added %s > %s' % (category.name, subcategory_Name))
                    return redirect(url_for('home'))
                else:
                    flash('Sub-Category already exists')
                    return redirect(url_for('addSubCategory',
                                            cat_Name=category.name))
            else:
                flash('Please provide a name and description for subcategory')
                return redirect(url_for('addSubCategory',
                                        cat_Name=category.name))
        else:
            # Render add sub category page
            return render_template('addSubCategory.html',
                                   cat_Name=category.name,
                                   categories=categories)


@app.route('/catalog/<category_param>/subcategory/delete/<int:subcategory_id>',
           methods=['GET', 'POST'])
@user_loggedin
def deleteSubCategory(category_param, subcategory_id):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        id=subcategory_id, category_id=category.id).first()
    if not subcategory:
        flash('Category/SubCategory not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = subcategory.name
        db_delete_commit(subcategory)
        flash('SubCategory deleted: %s > %s' % (category_param, name))
        return redirect(url_for('home'))
    else:
        return render_template('confirmDelete.html', item=subcategory.name)


@app.route('/catalog/<category_param>/subcategory/edit/<subcategory_param>',
           methods=['GET', 'POST'])
@user_loggedin
def editSubCategory(category_param, subcategory_param):
    categories = dbsession.query(Category).all()
    category = None
    # Get category from the passed parameter
    for item in categories:
        if item.name == category_param:
            category = item
            break

    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    if not subcategory:
        flash('Category/SubCategory not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        subcategory_name = request.form.get('sub_name')
        subcategory_desc = request.form.get('sub_description')
        category_name = request.form.get('cat_name')
        category_name = category_name and category_name.replace("+", " ")
        if subcategory_name and subcategory_desc and category_name:
            subcategory.name = subcategory_name
            subcategory.description = subcategory_desc
            if category_name != category_param:
                category = filter(lambda cat: cat.name ==
                                  category_name, categories)[0]
            subcategory.category_id = category and category.id
            dbsession.commit()
            flash('SubCategory updated %s > %s' %
                  (category_name, subcategory.name))
            return redirect(url_for('home'))
        else:
            flash('Please provide a name and description for subcategory')
            return redirect(url_for('editSubCategory',
                                    category_param=category_param,
                                    subcategory_param=subcategory_param))
    else:
        return render_template('editSubCategory.html',
                               subcategory=subcategory,
                               category_name=category.name,
                               categories=categories)

# CRUD operations for items


@app.route('/catalog/<category_param>/<subcategory_param>/<product_param>')
def showProduct(category_param, subcategory_param, product_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()
        if subcategory:
            product = dbsession.query(Product).filter_by(
                name=product_param, subcategory_id=subcategory.id).first()
            if product:
                brand = dbsession.query(Brand).filter_by(
                    id=product.brand_id).first()
                pic = dbsession.query(Product_Pics).filter_by(
                    product_id=product.id).first()
                product_specs = dbsession.query(Product_Specs).filter_by(
                    product_id=product.id).first()
                return render_template('showProduct.html',
                                       product=product,
                                       brand=brand,
                                       product_pic=pic.picture,
                                       product_specs=product_specs,
                                       category=category,
                                       subcategory=subcategory)
            else:
                flash('Invalid Product: %s' % product_param)
        else:
            flash('Invalid Sub-Category: %s' % subcategory_param)
    else:
        flash('Invalid Category: %s' % category_param)
    return redirect(url_for('home'))


@app.route('/catalog/<category_param>/<subcategory_param>/<brand_param>/products')
def showProductsByBrand(category_param, subcategory_param, brand_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()
        if subcategory:
            brand = dbsession.query(Brand).filter_by(
                name=brand_param, subcategory_id=subcategory.id).first()
            if brand:
                products = dbsession.query(Product).filter_by(
                    brand_id=brand.id, subcategory_id=subcategory.id).all()
                return render_template('showProductsByBrand.html',
                                       category=category,
                                       subcategory=subcategory,
                                       products=products)
            else:
                flash('Brand not found')
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))


@app.route('/catalog/<category_param>/<subcategory_param>/product/add',
           methods=['GET', 'POST'])
@user_loggedin
def addProduct(category_param, subcategory_param):
    # Get category from the passed parameter
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategories = category and dbsession.query(
        SubCategory).filter_by(category_id=category.id).all()
    subcategory = None

    # Get category from the passed parameter
    for item in subcategories:
        if item.name == subcategory_param:
            subcategory = item
            break

    # Don't proceed if the category or subcategory is invalid
    if not category or not subcategory:
        flash('Invalid category/subcategory')
        return redirect(url_for('home'))
    else:
        if(request.method == 'POST'):
            # Product Brand
            brand_name = request.form.get('brand_Name')

            # Product basics
            product_name = request.form.get('product_Name')
            product_desc = request.form.get('product_Description')

            # Product picture
            product_pic = request.form.get('product_Pic')

            # Product specifications
            model_number = request.form.get('model_Number')
            model_name = request.form.get('model_Name')
            product_color = request.form.get('product_Color')

            subcat_name = request.form.get('subcat_name')
            subcat_name = subcat_name and subcat_name.replace("+", " ")

            # Check if the user has entered name and description
            if product_name and product_desc and model_number and model_name and product_color and brand_name and subcat_name:
                if subcat_name != subcategory_param:
                    subcategory = filter(
                        lambda subcat: subcat.name == subcategory_name,
                        subcategories)[0]
                if not checkIfProductExists(subcategory.id, product_name):
                    # Check if brand already exists
                    brand = dbsession.query(Brand).filter_by(
                        name=brand_name).first()
                    if not brand:
                        brand = Brand(name=brand_name,
                                      subcategory_id=subcategory.id)
                        db_add_commit(brand)
                    if subcat_name != subcategory_param:
                        subcategory = filter(lambda: cat)
                    product = Product(name=product_name,
                                      description=product_desc,
                                      subcategory_id=subcategory.id,
                                      brand_id=brand.id,
                                      user_id=session['user_id'])
                    db_add_commit(product)
                    if product_pic:
                        pic = Product_Pics(
                            picture=product_pic, product_id=product.id)
                        db_add_commit(pic)
                    product_specs = Product_Specs(model_name=model_name,
                                                  model_number=model_number,
                                                  color=product_color,
                                                  product_id=product.id)
                    db_add_commit(product_specs)
                    flash('Added %s > %s > %s' %
                          (category.name, subcategory.name, product.name))
                    return redirect(url_for('home'))
                else:
                    flash('Product already exists')
                    return redirect(url_for('addProduct',
                                    category_param=category_param,
                                    subcategory_param=subcategory_param))
            else:
                flash('Fields marked with * are mandatory')
                return redirect(url_for('addProduct',
                                category_param=category_param,
                                subcategory_param=subcategory_param))
        else:
            # Render add product page
            return render_template('addProduct.html',
                                   subcategories=subcategories)


@app.route('/catalog/<category_param>/<subcategory_param>/product/delete/<int:product_id>',
           methods=['GET', 'POST'])
@user_loggedin
def deleteProduct(category_param, subcategory_param, product_id):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    product = subcategory and dbsession.query(Product).filter_by(
        id=product_id, subcategory_id=subcategory.id).first()
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = product.name
        db_delete_commit(product)
        flash('Product deleted: %s > %s > %s' %
              (category_param, subcategory_param, name))
        return redirect(url_for('home'))
    else:
        return render_template('confirmDelete.html', item=product.name)


@app.route('/catalog/<category_param>/<subcategory_param>/product/edit/<product_param>', methods=['GET', 'POST'])
@user_loggedin
def editProduct(category_param, subcategory_param, product_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategories = category and dbsession.query(
        SubCategory).filter_by(category_id=category.id).all()
    subcategory = None

    # Get category from the passed parameter
    for item in subcategories:
        if item.name == subcategory_param:
            subcategory = item
            break

    product = subcategory and dbsession.query(Product).filter_by(
        name=product_param, subcategory_id=subcategory.id).first()
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home'))
    brand = dbsession.query(Brand).filter_by(id=product.brand_id).first()
    pic = dbsession.query(Product_Pics).filter_by(
        product_id=product.id).first()
    product_specs = dbsession.query(
        Product_Specs).filter_by(product_id=product.id).first()
    if request.method == 'POST':
        # Product Brand
        brand_name = request.form.get('brand_name')

        # Product basics
        product_name = request.form.get('product_name')
        product_desc = request.form.get('product_description')

        # Product picture
        product_pic = request.form.get('product_pic')

        # Product specifications
        model_number = request.form.get('model_number')
        model_name = request.form.get('model_name')
        product_color = request.form.get('product_color')

        subcat_name = request.form.get('subcat_name')
        subcat_name = subcat_name and subcat_name.replace("+", " ")

        # Check if the user has entered name and description
        if product_name and product_desc and model_number and model_name and product_color and brand_name and subcat_name:
            if subcat_name != subcategory_param:
                subcategory = filter(
                    lambda subcat: subcat.name == subcategory_name,
                    subcategories)[0]
            if not checkIfProductExists(subcategory.id, product_name):
                product.name = product_name
                product.description = product_desc
                product.subcategory_id = subcategory.id

                # Check if new brand already exists
                if not brand:
                    brand = Brand(name=brand_name,
                                  subcategory_id=subcategory.id)
                if product_pic:
                    pic.picture = product_pic
                product_specs.model_name = model_name
                product_specs.model_number = model_number
                product_specs.color = product_color
                dbsession.commit()
                flash('Product updated %s > %s > %s' %
                      (category_param, subcategory_param, product.name))
                return redirect(url_for('home'))
            else:
                flash('Product already exists')
                return redirect(url_for('editProduct',
                                category_param=category_param,
                                subcategory_param=subcategory_param,
                                product_param=product_param))
        else:
            flash('Fields marked with * are mandatory')
            return redirect(url_for('editProduct',
                            category_param=category_param,
                            subcategory_param=subcategory_param,
                            product_param=product_param))
    else:
        return render_template('editProduct.html',
                               product=product,
                               product_pic=pic,
                               brand=brand,
                               product_specs=product_specs,
                               category_name=category.name,
                               subcategory_name=subcategory.name,
                               subcategories=subcategories)

# JSON


@app.route('/api/v1/catalog.json')
def getJSON():
    categories = dbsession.query(Category).all()
    dic = {}
    cdic = []
    sdic = []
    for item in categories:
        subcategory = dbsession.query(
            SubCategory).filter_by(category_id=item.id).all()
        temp = {'name': item.name, 'data': [
            i.serialize() for i in subcategory]}
        cdic.append(temp)
        for sub in subcategory:
            brand = dbsession.query(Brand).filter_by(
                subcategory_id=sub.id).all()
            temp = {'name': sub.name, 'data': [i.serialize() for i in brand]}
            sdic.append(temp)
    dic["Categories"] = cdic
    dic["Brands"] = sdic
    return jsonify(dic)


@app.route('/api/v1/catalog/categories.json')
def getCategoryJSON():
    categories = dbsession.query(Category).all()
    if not categories:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(categories=[i.serialize() for i in categories])


@app.route('/api/v1/catalog/<category_param>/subcategories.json')
def getSubCategoryJSON(category_param):
    category = dbsession.query(Category).first()
    subcategories = category and dbsession.query(
        SubCategory).filter_by(category_id=category.id).all()
    if not subcategories:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(subcategories=[i.serialize() for i in subcategories])


@app.route('/api/v1/catalog/<category_param>/<subcategory_param>/brands.json')
def getBrandJSON(category_param, subcategory_param):
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    brands = subcategory and dbsession.query(
        Brand).filter_by(subcategory_id=subcategory.id).all()
    if not brands:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(brands=[i.serialize() for i in brands])


@app.route('/api/v1/catalog/<category_param>/<subcategory_param>/products.json')
def getProductJSON(category_param, subcategory_param):
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    products = subcategory and dbsession.query(
        Product).filter_by(subcategory_id=subcategory.id).all()
    if not products:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(products=[i.serialize() for i in products])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
