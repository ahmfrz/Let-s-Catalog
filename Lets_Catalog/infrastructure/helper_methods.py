from .. models.category import Category
from .. models.subcategory import SubCategory
from .. models.product import Product
from .. models.user import User
from .. models.db_session import dbsession
from flask import session

def db_add_commit(entity):
    '''Add the entity to database and commit

    entity:
        The entity to be added to database
    '''
    dbsession.add(entity)
    dbsession.commit()


def db_delete_commit(entity):
    '''Delete the entity to database and commit

    entity:
        The entity to be deleted from database
    '''
    dbsession.delete(entity)
    dbsession.commit()


def checkIfCategoryExists(categoryName):
    '''Check if the category name is already used

    categoryName:
        The name of the category
    '''
    return dbsession.query(Category).filter_by(name=categoryName).first()


def checkIfSubCategoryExists(category_id, subcategoryName):
    '''Check if the subcategory name is already used under provided category

    category_id:
        The category id
    subcategoryName:
        The name of the subcategory
    '''
    return dbsession.query(SubCategory).filter_by(
        name=subcategoryName,
        category_id=category_id).first()


def checkIfProductExists(subcategory_id, productName):
    '''Check if the product name is already used under provided subcategory

    subcategory_id:
        The subcategory id
    productName:
        The name of the product
    '''
    return dbsession.query(Product).filter_by(
        name=productName,
        subcategory_id=subcategory_id).first()

# Adding new users


def createUser():
    '''Create new user after authentication'''
    newUser = User(name=session['username'], email=session['email'],
                   picture=session['picture'])
    dbsession.add(newUser)
    dbsession.commit()

    # Get the user id of new user
    user = dbsession.query(User).filter_by(email=session['email']).first()
    return user.id


def getUserInfo(user_id):
    '''Get user info for given user id

    user_id:
        The user id
    '''
    user = dbsession.query(User).filter_by(id=user_id).first()
    return user


def getUserId(email):
    '''Get user id from email address

    email:
        The email address of the user
    '''
    user = dbsession.query(User).filter_by(email=email).first()
    return user and user.id