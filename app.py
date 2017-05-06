from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Product, Product_Pics, Product_Specs, Category, Brand, SubCategory
from functools import wraps

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
            return redirect(url_for('login'))
    return decorated_function

def db_add_commit(entity):
    dbsession.add(entity)
    dbsession.commit()

def db_delete_commit(entity):
    dbsession.delete(entity)
    dbsession.commit()

@app.route('/index')
@app.route('/')
def home():
    return render_template('home.html')

# CRUD operations for category
@app.route('/catalog/<category>/<int:category_id>/items')
def showCategory(category, category_id):
    output = ""
    result = dbsession.query(SubCategory).filter_by(category_id=category_id).all()
    if result:
        for item in range(len(result)):
            output += "<h1>" + result[item].name + "</h1><br>"
    return output#render_template('category.html')

@app.route('/catalog/add_category', methods=['GET', 'POST'])
@user_loggedin
def addCategory():
    if request.method == 'POST':
        categoryName = request.form.get("CategoryName")
        if categoryName:
            newCategory = Category(name=categoryName)
            db_add_commit(newCategory)
            flash('New category added: %s' % newCategory.name)
            return render_template('home.html')
        else:
            flash('Category name must not be empty')
            return render_template('addCategory.html')
    else:
        return render_template('addCategory.html')

@app.route('/catalog/delete_category/<int:category_id>', methods=['POST'])
@user_loggedin
def deleteCategory(category_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(id=category_id).first()
        if category:
            name = category.name
            db_delete_commit(category)
            flash('Category deleted: %s' % name)
        else:
            flash('Category not found')
    return redirect(url_for('home'))

@app.route('/catalog/edit_category/<int:category_id>', methods=['GET', 'POST'])
@user_loggedin
def editCategory(category_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(id=category_id).first()
        if not category:
            flash('Category not found')
            return redirect(url_for('home'))
        name = request.form.get('CategoryName')
        if name:
            category.name = name
            flash('Category updated %s' % category.name)
        else:
            flash('Category name must not be empty')
            return render_template('editCategory.html')
    else:
        return render_template('editCategory.html')

# CRUD operations for sub category
@app.route('/catalog/<category_param>/<subcatagory_param>')
def showSubCategory(category_param, subcatagory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcatagory = dbsession.query(SubCategory).filter_by(name=subcatagory_param).first()
        if subcategory:
            return render_template('subcategory.html')
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))


@app.route('/catalog/<category_param>/add_subcategory', methods=['GET', 'POST'])
@user_loggedin
def addSubCategory(category_param):
    # Get category from the passed parameter
    category = dbsession.query(Category).filter_by(name=category_param).first()

    # Don't proceed if the category is invalid
    if not category:
        flash('Invalid category')
        return redirect(url_for('home'))
    else:
        if(request.method == 'POST'):
            subcategory_Name = request.form.get('sub_Name')
            subcategory_Desc = request.form.get('sub_Description')

            # Check if the user has entered name and description
            if subcategory_Name and subcategory_Desc:
                subcategory = SubCategory(name=subcategory_Name, description=subcatagory_Desc, category_id=category.id)
                db_add_commit(subcategory)
                flash('Added %s > %s' % (category.name, subcatagory.name))
                return redirect(url_for('home'))
            else:
                flash('Please provide a name and description for subcategory')
                return render_template('addSubCategory.html')
        else:
            # Render add sub category page
            return render_template('addSubCategory.html')

@app.route('/catalog/<category_param>/delete_subcategory/<int:subcategory_id>',
    methods=['GET', 'POST'])
@user_loggedin
def deleteSubCategory(category_param, subcategory_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(name=category_param).first()
        subcategory = dbsession.query(SubCategory).filter_by(id=subcategory_id, category_id=category.id).first()
        if subcategory:
            name = subcategory.name
            db_delete_commit(subcategory)
            flash('SubCategory deleted: %s > %s' % (category_param, name))
        else:
            flash('SubCategory not found')
    return redirect(url_for('home'))

@app.route('/catalog/<category_param>/edit_subcategory/<int:subcategory_id>',
    methods=['GET', 'POST'])
@user_loggedin
def editSubCategory(category_param, subcategory_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(name=category_param).first()
        subcategory = category and dbsession.query(SubCategory).filter_by(id=subcategory_id, category_id=category.id).first()
        if not subcategory:
            flash('Category/SubCategory not found')
            return redirect(url_for('home'))
        subcategory_name = request.form.get('sub_name')
        subcategory_desc = request.form.get('sub_description')
        if subcategory_name and subcategory_desc:
            subcategory.name = subcategory_name
            subcategory.description = subcategory_desc
            flash('SubCategory updated %s > %s' % (category_param, subcategory.name))
        else:
            flash('Please provide a name and description for subcategory')
            return render_template('editSubCategory.html')
    else:
        return render_template('editSubCategory.html')

# CRUD operations for items
@app.route('/catalog/<category_param>/<subcategory_param>/<product_param>')
def showProduct(category_param, subcatagory_param, product_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcatagory = dbsession.query(SubCategory).filter_by(name=subcatagory_param).first()
        if subcategory:
            product = dbsession.query(Product).filter_by(name=product_param).first()
            if product:
                return render_template('showProduct.html', product)
            else:
                flash('Invalid Product: %s' % product_param)
        else:
            flash('Invalid Sub-Category: %s' % subcatagory_param)
    else:
        flash('Invalid Category: %s' % category_param)
    return redirect(url_for('home'))

@app.route('/catalog/<category_param>/<subcategory_param>/add_item')
@user_loggedin
def addProduct(category_param, subcatagory_param):
    # Get category from the passed parameter
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcatagory_param, category_id=category.id).first()

    # Don't proceed if the category or subcategory is invalid
    if not category or not subcategory:
        flash('Invalid category/subcategory')
        return redirect(url_for('home'))
    else:
        if(request.method == 'POST'):
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

            # Check if the user has entered name and description
            if product_Name and product_Desc and model_number and model_name and product_color and brand_name:
                # Check if brand already exists
                brand = dbsession.query(Brand).filter_by(name=brand_name).first()
                if not brand:
                    brand = Brand(name=brand_name, subcategory_id=subcategory.id)
                    db_add_commit(brand)
                product = Product(name=product_Name, description=product_Desc, subcategory_id=subcategory.id, brand_id=brand.id)
                db_add_commit(product)
                if product_pic:
                    pic = Product_Pics(picture=product_pic, product_id=product.id)
                    db_add_commit(pic)
                product_specs = Product_Specs(model_name=model_name, model_number=model_number,
                    color=product_color, product_id=Product.id)
                db_add_commit(product_specs)
                flash('Added %s > %s > %s' % (category.name, subcatagory.name, product.name))
                return redirect(url_for('home'))
            else:
                flash('Fields marked with * are mandatory')
                return render_template('addProduct.html')
        else:
            # Render add product page
            return render_template('addProduct.html')

@app.route('/catalog/<category_param>/<subcategory_param>/delete_product/<int:product_id>')
@user_loggedin
def deleteProduct(category_param, subcategory_param, product_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(name=category_param).first()
        subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
        product = subcategory and dbsession.query(Product).filter_by(id=product_id, subcategory_id=subcategory.id).first()
        if product:
            name = product.name
            db_delete_commit(product)
            flash('Product deleted: %s > %s > %s' % (category_param, subcategory_param, name))
        else:
            flash('Category/SubCategory/Product not found')
    return redirect(url_for('home'))

@app.route('/catalog/<category_param>/<subcategory_param>/edit_item/<int:product_id>')
@user_loggedin
def editProduct(category_param, subcategory_param, product_id):
    if request.method == 'POST':
        category = dbsession.query(Category).filter_by(name=category_param).first()
        subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_id, category_id=category.id).first()
        product = subcategory and dbsession.query(Product).filter_by(id=product_id, subcategory_id=subcategory.id).first()
        if not product:
            flash('Category/SubCategory/Product not found')
            return redirect(url_for('home'))

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

        # Check if the user has entered name and description
        if product_Name and product_Desc and model_number and model_name and product_color and brand_name:
            product.name = product_name
            product.description = product_desc

            # Check if new brand already exists
            brand = dbsession.query(Brand).filter_by(name=brand_name).first()
            if not brand:
                brand = Brand(name=brand_name, subcategory_id=subcategory.id)
            if product_pic:
                pic = dbsession.query(Product_Pics).filter_by(product_id=product.id)
                pic.picture = Product_pic
            product_specs = dbsession.query(Product_Specs).filter_by(product_id=product.id)
            product_specs.model_name=model_name
            product_specs.model_number=model_number,
            product_specs.color=product_color
            flash('Product updated %s > %s > %s' % (category_param, subcategory_param, product.name))
        else:
            flash('Fields marked with * are mandatory')
            return render_template('editProduct.html')
    else:
        return render_template('editProduct.html')

# JSON
@app.route('/catalog.json')
def getJSON():
    return "JSON"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)