"""Defines subcategory CRUD endpoints"""

from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.product import Product
from .. models.db_session import dbsession
from .. infrastructure import helper_methods, decorators
from flask import render_template, Blueprint, session, redirect, flash, request
from flask import url_for, request

subcategory_page = Blueprint('subcategory_page', __name__,
                             template_folder='templates')

# CRUD operations for sub category


@subcategory_page.route('/catalog/<category_param>/<subcategory_param>')
def showSubCategory(category_param, subcategory_param):
    '''Display the given subcategory

    category_param:
        The name of category
    subcategory_param:
        The name of subcategory to be displayed
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()

    # Check if the category exists
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()

        # Check if the subcategory exists under the given category
        if subcategory:
            products = dbsession.query(Product).filter_by(
                subcategory_id=subcategory.id).all()
            return render_template('showSubCategory.html', category=category,
                                   subcategory=subcategory, products=products)
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home_page.home'))


@subcategory_page.route('/catalog/<category_param>/<subcategory_param>/brands')
def showSubCategoryBrand(category_param, subcategory_param):
    '''Display the given subcategory by brand

    category_param:
        The name of category
    subcategory_param:
        The name of subcategory to be displayed
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()

    # Check if the category exists
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()

        # Check if the subcategory exists under the given category
        if subcategory:
            # Get all brands under that subcategory
            brands = dbsession.query(Brand).filter_by(
                subcategory_id=subcategory.id).all()
            return render_template('showBrand.html', category=category,
                                   subcategory=subcategory, brands=brands)
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home_page.home'))


@subcategory_page.route('/catalog/<category_param>/subcategory/add',
                        methods=['GET', 'POST'])
@decorators.user_loggedin
def addSubCategory(category_param):
    '''Add a new subcategory

    category_param:
        The name of parent category'''
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
        return redirect(url_for('home_page.home'))
    else:
        if(request.method == 'POST'):
            # Get subcategory data from request
            subcategory_Name = request.form.get('sub_Name')
            subcategory_Desc = request.form.get('sub_Description')
            category_name = request.form.get('cat_name')
            category_name = category_name and category_name.replace("+", " ")

            # Check if the user has entered name and description and selected a
            # category
            if subcategory_Name and subcategory_Desc and category_name:
                # Check if the user has changed original category
                if category_name != category_param:
                    category = filter(lambda cat: cat.name ==
                                      category_name, categories)[0]

                # Check if the subcategory name is taken
                if not helper_methods.checkIfSubCategoryExists(
                        category.id, subcategory_Name):
                    subcategory = SubCategory(
                        name=subcategory_Name, description=subcategory_Desc,
                        category_id=category.id, user_id=session['user_id'])
                    helper_methods.db_add_commit(subcategory)
                    flash('Added %s > %s' % (category.name, subcategory_Name))
                    return redirect(url_for('home_page.home'))
                else:
                    flash('Sub-Category already exists')
                    return redirect(url_for('subcategory_page.addSubCategory',
                                            cat_Name=category.name))
            else:
                flash('Please provide a name and description for subcategory')
                return redirect(url_for('subcategory_page.addSubCategory',
                                        cat_Name=category.name))
        else:
            # Render add sub category page
            return render_template('addSubCategory.html',
                                   cat_Name=category.name,
                                   categories=categories)


@subcategory_page.route(
    '/catalog/<category_param>/subcategory/delete/<int:subcategory_id>',
    methods=['GET', 'POST'])
@decorators.user_loggedin
def deleteSubCategory(category_param, subcategory_id):
    '''Delete the given subcategory

    category_param:
        The parent category

    subcategory_id:
        The subcategory to be deleted'''
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        id=subcategory_id, category_id=category.id).first()

    # Check if the subcategory exists
    if not subcategory:
        flash('Category/SubCategory not found')
        return redirect(url_for('home_page.home'))
    if request.method == 'POST':
        name = subcategory.name
        helper_methods.db_delete_commit(subcategory)
        flash('SubCategory deleted: %s > %s' % (category_param, name))
        return redirect(url_for('home_page.home'))
    else:
        return render_template('confirmDelete.html', item=subcategory.name)


@subcategory_page.route(
    '/catalog/<category_param>/subcategory/edit/<subcategory_param>',
    methods=['GET', 'POST'])
@decorators.user_loggedin
def editSubCategory(category_param, subcategory_param):
    '''Edit the given subcategory

    category_param:
        The parent category

    subcategory_id:
        The subcategory to be edited'''
    categories = dbsession.query(Category).all()
    category = None

    # Get category from the passed parameter
    for item in categories:
        if item.name == category_param:
            category = item
            break

    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()

    # Check if the subcategory exists
    if not subcategory:
        flash('Category/SubCategory not found')
        return redirect(url_for('home_page.home'))
    if request.method == 'POST':
        # Get the subcategory data from request
        subcategory_name = request.form.get('sub_name')
        subcategory_desc = request.form.get('sub_description')
        category_name = request.form.get('cat_name')
        category_name = category_name and category_name.replace("+", " ")
        if subcategory_name and subcategory_desc and category_name:
            # Check if the user has changed the original category
            if category_name != category_param:
                category = filter(lambda cat: cat.name ==
                                  category_name, categories)[0]
            # Check if the subcategory name is taken
            if subcategory_name == subcategory_param or not helper_methods.checkIfSubCategoryExists(
                    category.id, subcategory_name):
                subcategory.name = subcategory_name
                subcategory.description = subcategory_desc
                subcategory.category_id = category and category.id
                dbsession.commit()
                flash('SubCategory updated %s > %s' %
                      (category_name, subcategory.name))
                return redirect(url_for('home_page.home'))
            else:
                flash('Sub-Category already exists')
                return redirect(url_for('subcategory_page.editSubCategory',
                                        category_param=category_param,
                                        subcategory_param=subcategory_param))
        else:
            flash('Please provide a name and description for subcategory')
            return redirect(url_for('subcategory_page.editSubCategory',
                                    category_param=category_param,
                                    subcategory_param=subcategory_param))
    else:
        return render_template('editSubCategory.html',
                               subcategory=subcategory,
                               category_name=category.name,
                               categories=categories)
