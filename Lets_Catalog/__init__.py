"""Defines application and all blueprints"""

from flask import Flask
import views

app = Flask(__name__)
app.register_blueprint(views.home.home_page)
app.register_blueprint(views.oauth.oauth_page)
app.register_blueprint(views.category.category_page)
app.register_blueprint(views.subcategory.subcategory_page)
app.register_blueprint(views.product.product_page)
app.register_blueprint(views.json_endpoint.json_page)
app.secret_key = 'super_secret_key'

if __name__ == "__main__":
    app.run()

__author__ = "Ahmed Faraz Ansari"
__copyright__ = "Copyright 2017 (c) ahmfrz"

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ahmed Faraz Ansari"
__email__ = "af.ahmfrz@gmail.com"
__status__ = "Development"