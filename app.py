from flask import Flask, make_response, render_template, jsonify, request, redirect, url_for, session, flash
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
            session['last_URL'] = request.url_rule
            return redirect(url_for('login'))
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
    return dbsession.query(SubCategory).filter_by(name=subcategoryName,category_id=category_id).first()

def checkIfProductExists(subcategory_id, productName):
    return dbsession.query(Product).filter_by(name=productName,subcategory_id=subcategory_id).first()

@app.route('/index')
@app.route('/')
def home():
    items = dbsession.query(Category, SubCategory, Product, Product_Pics).join(SubCategory, Product, Product_Pics).limit(3).all()
    session['username'] = "Blah"
    return render_template('home.html', items=items, count=len(items))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for(session['last_URL']))
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

# CRUD operations for category
@app.route('/catalog/<category_param>/')
def showCategory(category_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategories = dbsession.query(SubCategory).filter_by(category_id=category.id).all()
        return render_template('showCategory.html', category=category, subcategories=subcategories)
    else:
        flash('Category not found')
        return redirect(url_for('home'))

@app.route('/catalog/add_category', methods=['GET', 'POST'])
@user_loggedin
def addCategory():
    if request.method == 'POST':
        categoryName = request.form.get("cat_name")
        if categoryName:
            if not checkIfCategoryExists(categoryName):
                newCategory = Category(name=categoryName)
                db_add_commit(newCategory)
                flash('New category added: %s' % newCategory.name)
                return redirect(url_for('home'))
            else:
                flash('Category already exists')
                return render_template('addCategory.html')
        else:
            flash('Category name must not be empty')
            return render_template('addCategory.html')
    else:
        return render_template('addCategory.html')

@app.route('/catalog/delete_category/<int:category_id>', methods=['GET','POST'])
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

@app.route('/catalog/edit_category/<int:category_id>', methods=['GET', 'POST'])
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
        else:
            flash('Category name must not be empty')
            return render_template('editCategory.html')
    else:
        return render_template('editCategory.html', category=category)

# CRUD operations for sub category
@app.route('/catalog/<category_param>/<subcategory_param>')
def showSubCategory(category_param, subcategory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
        if subcategory:
            products = dbsession.query(Product).filter_by(subcategory_id=subcategory.id).all()
            return render_template('showSubCategory.html', category=category, subcategory=subcategory, products=products)
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))

@app.route('/catalog/<category_param>/<subcategory_param>/brands')
def showSubCategoryBrand(category_param, subcategory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
        if subcategory:
            brands = dbsession.query(Brand).filter_by(subcategory_id=subcategory.id).all()
            return render_template('showBrand.html', category=category, subcategory=subcategory, brands=brands)
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
                if not checkIfSubCategoryExists(category.id, subcategory_Name):
                    subcategory = SubCategory(name=subcategory_Name, description=subcategory_Desc, category_id=category.id)
                    db_add_commit(subcategory)
                    flash('Added %s > %s' % (category.name, subcategory_Name))
                    return redirect(url_for('home'))
                else:
                    flash('Sub-Category already exists')
                    return render_template('addSubCategory.html', cat_Name=category.name)
            else:
                flash('Please provide a name and description for subcategory')
                return render_template('addSubCategory.html', cat_Name=category.name)
        else:
            # Render add sub category page
            return render_template('addSubCategory.html', cat_Name=category.name)

@app.route('/catalog/<category_param>/delete_subcategory/<int:subcategory_id>',
    methods=['GET', 'POST'])
@user_loggedin
def deleteSubCategory(category_param, subcategory_id):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(id=subcategory_id, category_id=category.id).first()
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

@app.route('/catalog/<category_param>/edit_subcategory/<subcategory_param>',
    methods=['GET', 'POST'])
@user_loggedin
def editSubCategory(category_param, subcategory_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
    if not subcategory:
        flash('Category/SubCategory not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        subcategory_name = request.form.get('sub_name')
        subcategory_desc = request.form.get('sub_description')
        if subcategory_name and subcategory_desc:
            subcategory.name = subcategory_name
            subcategory.description = subcategory_desc
            flash('SubCategory updated %s > %s' % (category_param, subcategory.name))
            return redirect(url_for('home'))
        else:
            flash('Please provide a name and description for subcategory')
            return render_template('editSubCategory.html', subcategory=subcategory, category_name=category.name)
    else:
        return render_template('editSubCategory.html', subcategory=subcategory, category_name=category.name)

# CRUD operations for items
@app.route('/catalog/<category_param>/<subcategory_param>/<product_param>')
def showProduct(category_param, subcategory_param, product_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    if category:
        subcategory = dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
        if subcategory:
            product = dbsession.query(Product).filter_by(name=product_param, subcategory_id=subcategory.id).first()
            if product:
                brand = dbsession.query(Brand).filter_by(id=product.brand_id).first()
                pic = dbsession.query(Product_Pics).filter_by(product_id=product.id)
                product_specs = dbsession.query(Product_Specs).filter_by(product_id=product.id)
                return render_template('showProduct.html', product=product, brand=brand, product_pic=pic, product_specs=product_specs, category=category, subcategory=subcategory)
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
        subcategory = dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
        if subcategory:
            brand = dbsession.query(Brand).filter_by(name=brand_param, subcategory_id=subcategory.id).first()
            if brand:
                products = dbsession.query(Product).filter_by(brand_id=brand.id, subcategory_id=subcategory.id).all()
                return render_template('showProductsByBrand.html', category=category, subcategory=subcategory, products=products)
            else:
                flash('Brand not found')
        else:
            flash('Sub-Category not found')
    else:
        flash('Category not found')
    return redirect(url_for('home'))

@app.route('/catalog/<category_param>/<subcategory_param>/add_product', methods=['GET','POST'])
@user_loggedin
def addProduct(category_param, subcategory_param):
    # Get category from the passed parameter
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()

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
            # Check if the user has entered name and description
            if product_name and product_desc and model_number and model_name and product_color and brand_name:
                if not checkIfProductExists(subcategory.id, product_name):
                    # Check if brand already exists
                    brand = dbsession.query(Brand).filter_by(name=brand_name).first()
                    if not brand:
                        brand = Brand(name=brand_name, subcategory_id=subcategory.id)
                        db_add_commit(brand)
                    product = Product(name=product_name, description=product_desc, subcategory_id=subcategory.id, brand_id=brand.id)
                    db_add_commit(product)
                    if product_pic:
                        pic = Product_Pics(picture=product_pic, product_id=product.id)
                        db_add_commit(pic)
                    product_specs = Product_Specs(model_name=model_name, model_number=model_number,
                        color=product_color, product_id=product.id)
                    db_add_commit(product_specs)
                    flash('Added %s > %s > %s' % (category.name, subcategory.name, product.name))
                    return redirect(url_for('home'))
                else:
                    flash('Product already exists')
                    return render_template('addProduct.html')
            else:
                flash('Fields marked with * are mandatory')
                return render_template('addProduct.html')
        else:
            # Render add product page
            return render_template('addProduct.html')

@app.route('/catalog/<category_param>/<subcategory_param>/delete_product/<int:product_id>', methods=['GET', 'POST'])
@user_loggedin
def deleteProduct(category_param, subcategory_param, product_id):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
    product = subcategory and dbsession.query(Product).filter_by(id=product_id, subcategory_id=subcategory.id).first()
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = product.name
        db_delete_commit(product)
        flash('Product deleted: %s > %s > %s' % (category_param, subcategory_param, name))
        return redirect(url_for('home'))
    else:
        return render_template('confirmDelete.html', item=product.name)

@app.route('/catalog/<category_param>/<subcategory_param>/edit_item/<product_param>', methods=['GET','POST'])
@user_loggedin
def editProduct(category_param, subcategory_param, product_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
    product = subcategory and dbsession.query(Product).filter_by(name=product_param, subcategory_id=subcategory.id).first()
    if not product:
        flash('Category/SubCategory/Product not found')
        return redirect(url_for('home'))
    brand = dbsession.query(Brand).filter_by(id=product.brand_id).first()
    pic = dbsession.query(Product_Pics).filter_by(product_id=product.id)
    product_specs = dbsession.query(Product_Specs).filter_by(product_id=product.id)
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

        # Check if the user has entered name and description
        if product_name and product_desc and model_number and model_name and product_color and brand_name:
            product.name = product_name
            product.description = product_desc

            # Check if new brand already exists
            if not brand:
                brand = Brand(name=brand_name, subcategory_id=subcategory.id)
            if product_pic:
                pic.picture = Product_pic
            product_specs.model_name=model_name
            product_specs.model_number=model_number,
            product_specs.color=product_color
            flash('Product updated %s > %s > %s' % (category_param, subcategory_param, product.name))
            return redirect(url_for('home'))
        else:
            flash('Fields marked with * are mandatory')
            return render_template('editProduct.html', product=product, product_pic=pic, brand=brand, product_specs=product_specs, category_name=category.name, subcategory_name=subcategory.name)
    else:
        return render_template('editProduct.html', product=product, product_pic=pic, brand=brand, product_specs=product_specs, category_name=category.name, subcategory_name=subcategory.name)

# JSON
@app.route('/catalog.json')
def getJSON():
    categories = dbsession.query(Category).all()
    dic = {}
    cdic = []
    sdic = []
    for item in categories:
        subcategory = dbsession.query(SubCategory).filter_by(category_id=item.id).all()
        temp = {'name': item.name, 'data': [i.serialize() for i in subcategory]}
        cdic.append(temp)
        for sub in subcategory:
            brand = dbsession.query(Brand).filter_by(subcategory_id=sub.id).all()
            temp = {'name': sub.name, 'data': [i.serialize() for i in brand]}
            sdic.append(temp)
    dic["Categories"] = cdic
    dic["Brands"] = sdic
    return jsonify(dic)

@app.route('/catalog/categories.json')
def getCategoryJSON():
    categories = dbsession.query(Category).all()
    if not categories:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(categories=[i.serialize() for i in categories])


@app.route('/catalog/<category_param>/subcategories.json')
def getSubCategoryJSON(category_param):
    category = dbsession.query(Category).first()
    subcategories = category and dbsession.query(SubCategory).filter_by(category_id=category.id).all()
    if not subcategories:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(subcategories=[i.serialize() for i in subcategories])

@app.route('/catalog/<category_param>/<subcategory_param>/brands.json')
def getBrandJSON(category_param, subcategory_param):
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name=subcategory_param, category_id=category.id).first()
    brands = subcategory and dbsession.query(Brand).filter_by(subcategory_id=subcategory.id).all()
    if not brands:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(brands=[i.serialize() for i in brands])

@app.route('/catalog/<category_param>/<subcategory_param>/products.json')
def getProductJSON(category_param, subcategory_param):
    category = dbsession.query(Category).first()
    subcategory = category and dbsession.query(SubCategory).filter_by(name= subcategory_param,category_id=category.id).first()
    products = subcategory and dbsession.query(Product).filter_by(subcategory_id=subcategory.id).all()
    if not products:
        return make_response(json.dumps('Invalid URL'), 401)
    return jsonify(products=[i.serialize() for i in products])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)