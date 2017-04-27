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
            dbsession.add(newCategory)
            dbsession.commit()
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
            dbsession.delete(category)
            dbsession.commit()
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


@app.route('/catalog/<category_param>/add_subcategory')
@user_loggedin
def addSubCategory(category_param):
    category = dbsession.query(Category).filter_by(name=category_param).first()
    return render_template('addSubCategory.html')

@app.route('/catalog/<category>/delete_subcategory/<int:subcategory_id>')
@user_loggedin
def deleteSubCategory(category, subcategory_id):
    return redirect(url_for('home'))

@app.route('/catalog/<category>/edit_subcategory/<int:subcategory_id>')
@user_loggedin
def editSubCategory(category, subcategory_id):
    return render_template('editSubCategory.html')

# CRUD operations for items
@app.route('/catalog/<category>/<subcategory>/<item>')
def showItem(category, subcatagory, item):
    return render_template('showItem.html')

@app.route('/catalog/<category>/<subcategory>/add_item')
@user_loggedin
def addItem(category, subcatagory):
    return render_template('additem.html')

@app.route('/catalog/<category>/<subcategory>/delete_item/<int:item_id>')
@user_loggedin
def deleteItem(category, subcategory_id, item_id):
    return redirect(url_for('home'))

@app.route('/catalog/<category>/<subcategory>/edit_item/<int:item_id>')
@user_loggedin
def editItem(category, subcategory, item_id):
    return render_template('editItem.html')

# JSON
@app.route('/catalog.json')
def getJSON():
    return "JSON"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)