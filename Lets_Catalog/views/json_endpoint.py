"""Defines JSON endpoints"""

import json
from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.product import Product
from .. models.brand import Brand
from .. models.product_pics import Product_Pics
from .. models.product_specs import Product_Specs
from .. models.db_session import dbsession
from .. infrastructure import helper_methods
from flask import render_template, Blueprint, session, redirect, jsonify, make_response

json_page = Blueprint('json_page', __name__,
                      template_folder='templates')


# JSON

@json_page.route('/api/v1/catalog.json')
def getJSON():
    '''Get all catalog items'''
    categories = dbsession.query(Category).all()
    dic = {}
    cdic = []
    sdic = []

    # Format data
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


@json_page.route('/api/v1/catalog/categories.json')
def getCategoryJSON():
    '''Get all categories'''
    categories = dbsession.query(Category).all()
    if not categories:
        return make_response(json.dumps('No categories found'), 401)
    return jsonify(categories=[i.serialize() for i in categories])


@json_page.route('/api/v1/catalog/<category_param>/subcategories.json')
def getSubCategoryJSON(category_param):
    '''Get all subcategories for given category'''
    category = dbsession.query(Category).first()
    subcategories = category and dbsession.query(
        SubCategory).filter_by(category_id=category.id).all()
    if not subcategories:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(subcategories=[i.serialize() for i in subcategories])


@json_page.route('/api/v1/catalog/<category_param>/<subcategory_param>/brands.json')
def getBrandJSON(category_param, subcategory_param):
    '''Get all brands under the given category and subcategory'''
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    brands = subcategory and dbsession.query(
        Brand).filter_by(subcategory_id=subcategory.id).all()
    if not brands:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(brands=[i.serialize() for i in brands])


@json_page.route(
    '/api/v1/catalog/<category_param>/<subcategory_param>/products.json')
def getProductJSON(category_param, subcategory_param):
    '''Get all products under given category and subcategory'''
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    products = subcategory and dbsession.query(
        Product).filter_by(subcategory_id=subcategory.id).all()
    if not products:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(products=[i.serialize() for i in products])
