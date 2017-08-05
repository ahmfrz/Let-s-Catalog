"""Defines product CRUD endpoints"""

from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.product import Product
from .. models.brand import Brand
from .. models.product_pics import Product_Pics
from .. models.product_specs import Product_Specs
from .. models.db_session import dbsession
from .. infrastructure import helper_methods, decorators
from flask import render_template, Blueprint, session, redirect, flash
from flask import url_for, request

product_page = Blueprint('product_page', __name__,
                         template_folder='templates')

# CRUD operations for items


@product_page.route(
    '/catalog/<category_param>/<subcategory_param>/<product_param>')
def showProduct(category_param, subcategory_param, product_param):
    '''Display the given product

    category_param:
        The category name

    subcategory_param:
        The parent subcategory

    product_param:
        The name of the product to be displayed
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()

    # Check if the category exists
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()

        # Check if the subcategory exists under the given category
        if subcategory:
            product = dbsession.query(Product).filter_by(
                name=product_param, subcategory_id=subcategory.id).first()

            # Check if the product exists under the given subcategory
            if product:
                # Get product related data
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
    return redirect(url_for('home_page.home'))


@product_page.route(
    '/catalog/<category_param>/<subcategory_param>/<brand_param>/products')
def showProductsByBrand(category_param, subcategory_param, brand_param):
    '''Display the products by brand

    category_param:
        The category name

    subcategory_param:
        The parent subcategory

    brand_param:
        The name of the brand
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()

    # Check if the category exists
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(
            name=subcategory_param, category_id=category.id).first()

        # Check if the subcategory exists under given category
        if subcategory:
            brand = dbsession.query(Brand).filter_by(
                name=brand_param, subcategory_id=subcategory.id).first()

            # Check if the brand exists under the given subcategory
            if brand:
                # Get all products under the given brand
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
    return redirect(url_for('home_page.home'))


@product_page.route(
    '/catalog/<category_param>/<subcategory_param>/product/add',
    methods=['GET', 'POST'])
@decorators.user_loggedin
def addProduct(category_param, subcategory_param):
    '''Add new product

    category_param:
        The name of the category

    subcategory_param:
        The name of the subcategory
    '''
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
        return redirect(url_for('home_page.home'))
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

            # Check if the user has entered required data
            if (product_name and product_desc and model_number and
                    model_name and product_color and brand_name and
                    subcat_name):
                # Check if the user has changed original subcategory
                if subcat_name != subcategory_param:
                    subcategory = filter(
                        lambda subcat: subcat.name == subcategory_name,
                        subcategories)[0]

                # Check if the product name is taken
                if not helper_methods.checkIfProductExists(
                        subcategory.id, product_name):
                    # Check if brand already exists
                    brand = dbsession.query(Brand).filter_by(
                        name=brand_name).first()
                    if not brand:
                        # Create new brand if it does not exist
                        brand = Brand(name=brand_name,
                                      subcategory_id=subcategory.id)
                        helper_methods.db_add_commit(brand)
                    product = Product(name=product_name,
                                      description=product_desc,
                                      subcategory_id=subcategory.id,
                                      brand_id=brand.id,
                                      user_id=session['user_id'])
                    helper_methods.db_add_commit(product)
                    if product_pic:
                        pic = Product_Pics(
                            picture=product_pic, product_id=product.id)
                        helper_methods.db_add_commit(pic)
                    product_specs = Product_Specs(model_name=model_name,
                                                  model_number=model_number,
                                                  color=product_color,
                                                  product_id=product.id)
                    helper_methods.db_add_commit(product_specs)
                    flash('Added %s > %s > %s' %
                          (category.name, subcategory.name, product.name))
                    return redirect(url_for('home_page.home'))
                else:
                    flash('Product already exists')
                    return redirect(url_for(
                        'product_page.addProduct',
                        category_param=category_param,
                        subcategory_param=subcategory_param))
            else:
                flash('Fields marked with * are mandatory')
                return redirect(url_for('product_page.addProduct',
                                        category_param=category_param,
                                        subcategory_param=subcategory_param))
        else:
            # Render add product page
            return render_template('addProduct.html',
                                   subcategories=subcategories)


@product_page.route(
    '/catalog/<category_param>/<subcategory_param>/product/delete/<int:product_id>',
    methods=['GET', 'POST'])
@decorators.user_loggedin
def deleteProduct(category_param, subcategory_param, product_id):
    '''Delete the given product

    category_param:
        The name of the category

    subcategory_param:
        The name of the subcategory

    product_id:
        The product id to be deleted
    '''
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(
        name=subcategory_param, category_id=category.id).first()
    product = subcategory and dbsession.query(Product).filter_by(
        id=product_id, subcategory_id=subcategory.id).first()

    # Check if the product exists
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home_page.home'))
    if request.method == 'POST':
        name = product.name
        helper_methods.db_delete_commit(product)
        flash('Product deleted: %s > %s > %s' %
              (category_param, subcategory_param, name))
        return redirect(url_for('home_page.home'))
    else:
        return render_template('confirmDelete.html', item=product.name)


@product_page.route(
    '/catalog/<category_param>/<subcategory_param>/product/edit/<product_param>',
    methods=['GET', 'POST'])
@decorators.user_loggedin
def editProduct(category_param, subcategory_param, product_param):
    '''Edit the given product

    category_param:
        The name of the category

    subcategory_param:
        The name of the subcategory

    product_param:
        The name of the product to be edited
    '''
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

    # Check if the product exists
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home_page.home'))

    # Get product related data
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
        if (product_name and product_desc and model_number and
                model_name and product_color and brand_name and subcat_name):
            # Check if the user has changed the original subcategory
            if subcat_name != subcategory_param:
                subcategory = filter(
                    lambda subcat: subcat.name == subcategory_name,
                    subcategories)[0]

            # Check if the product name is taken under this subcategory
            if product_name == product_param or not helper_methods.checkIfProductExists(
                    subcategory.id, product_name):
                product.name = product_name
                product.description = product_desc
                product.subcategory_id = subcategory.id

                # Check if new brand already exists
                if not brand:
                    brand = Brand(name=brand_name,
                                  subcategory_id=subcategory.id)
                if product_pic:
                    if not pic:
                        pic = Product_Pics(
                            picture=product_pic, product_id=product.id)
                        helper_methods.db_add_commit(pic)
                    else:
                        pic.picture = product_pic
                product_specs.model_name = model_name
                product_specs.model_number = model_number
                product_specs.color = product_color
                dbsession.commit()
                flash('Product updated %s > %s > %s' %
                      (category_param, subcategory_param, product.name))
                return redirect(url_for('home_page.home'))
            else:
                flash('Product already exists')
                return redirect(url_for('product_page.editProduct',
                                        category_param=category_param,
                                        subcategory_param=subcategory_param,
                                        product_param=product_param))
        else:
            flash('Fields marked with * are mandatory')
            return redirect(url_for('product_page.editProduct',
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
