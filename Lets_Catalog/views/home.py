"""Defines home endpoint"""

import string
import random
from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.product import Product
from .. models.product_pics import Product_Pics
from .. models.db_session import dbsession
from flask import render_template, Blueprint, session, redirect

home_page = Blueprint('home_page', __name__,
                      template_folder='templates')


@home_page.route('/index')
@home_page.route('/')
def home():
    '''Display the home page'''

    # Create a random state string to prevent CSRF
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state

    # Check if user was trying to access a page before logging in
    if 'username' in session and 'last_URL' in session:
        url = session['last_URL']
        del session['last_URL']
        return redirect(url)

    # Get last 5 items for home page
    items = dbsession.query(Category, SubCategory, Product, Product_Pics).join(
        SubCategory, Product, Product_Pics).order_by(
        Category.created_date).limit(5).all()
    return render_template('home.html', items=items, count=len(items),
                           STATE=session['state'])
