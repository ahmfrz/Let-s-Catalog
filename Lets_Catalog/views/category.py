"""Defines category CRUD endpoints"""

from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.db_session import dbsession
from flask import render_template, Blueprint, session, redirect, flash
from flask import url_for, request
from .. infrastructure import decorators, helper_methods

category_page = Blueprint('category_page', __name__,
                          template_folder='templates')

# CRUD operations for category


@category_page.route('/catalog/<category_param>/')
def showCategory(category_param):
    '''Display the requested category

    category_param:
        The category name to be displayed
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategories = dbsession.query(SubCategory).filter_by(
            category_id=category.id).all()
        return render_template('showCategory.html', category=category,
                               subcategories=subcategories)
    else:
        flash('Category not found')
        return redirect(url_for('home_page.home'))


@category_page.route('/catalog/user_categories')
@decorators.user_loggedin
def showUserCategory():
    '''Display categories created by logged in user'''
    category = dbsession.query(Category).filter_by(
        user_id=session['user_id']).all()
    if category:
        return render_template('showAllCategories.html', categories=category)
    else:
        flash('You have not created any categories')
        return redirect(url_for('home_page.home'))


@category_page.route('/catalog/category/add', methods=['GET', 'POST'])
@decorators.user_loggedin
def addCategory():
    '''Add new category'''
    if request.method == 'POST':
        categoryName = request.form.get("cat_name")

        # Check if user has provided a category name
        if categoryName:
            # Check if the category name is taken
            if not helper_methods.checkIfCategoryExists(categoryName):
                newCategory = Category(
                    name=categoryName, user_id=session['user_id'])
                helper_methods.db_add_commit(newCategory)
                flash('New category added: %s' % newCategory.name)
                return redirect(url_for('home_page.home'))
            else:
                # Category exists, redisplay the form for user to update
                flash('Category already exists')
                return redirect(url_for('category_page.addCategory'))
        else:
            flash('Category name must not be empty')
            return redirect(url_for('category_page.addCategory'))
    else:
        return render_template('addCategory.html')


@category_page.route('/catalog/category/delete/<int:category_id>',
                     methods=['GET', 'POST'])
@decorators.user_loggedin
def deleteCategory(category_id):
    '''Delete the given category

    category_id:
        The category id to be deleted
    '''
    category = dbsession.query(Category).filter_by(id=category_id).first()

    # Check if the category id related to a category in db
    if not category:
        flash('Category not found')
        return redirect(url_for('home_page.home'))
    if request.method == 'POST':
        name = category.name
        helper_methods.db_delete_commit(category)
        flash('Category deleted: %s' % name)
        return redirect(url_for('home_page.home'))
    else:
        return render_template('confirmDelete.html', item=category.name)


@category_page.route('/catalog/category/edit/<int:category_id>',
                     methods=['GET', 'POST'])
@decorators.user_loggedin
def editCategory(category_id):
    '''Edit the given category

    category_id:
        The category id to be edited
    '''
    category = dbsession.query(Category).filter_by(id=category_id).first()

    # Check if the category id related to a category in db
    if not category:
        flash('Category not found')
        return redirect(url_for('home_page.home'))
    if request.method == 'POST':
        name = request.form.get('cat_Name')
        if name:
            # Check if the category name is taken
            if name == category.name or not helper_methods.checkIfCategoryExists(name):
                category.name = name
                flash('Category updated %s' % category.name)
                return redirect(url_for('home_page.home'))
            else:
                # Category exists, redisplay the form for user to update
                flash('Category already exists')
                return redirect(url_for('category_page.editCategory',
                                        category_id=category_id))
        else:
            flash('Category name must not be empty')
            return redirect(url_for('category_page.editCategory',
                                    category_id=category_id))
    else:
        return render_template('editCategory.html', category=category)
