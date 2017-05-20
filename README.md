# Let-s-Catalog
Catalog application in Flask with SqlAlchemy
 
## What is it?
 Catalog application where users can add and share their favorite catalog items
 
## Features
 * Uses Flask
 * Uses OAuth2
 * Uses SQLAlchemy
 * Prevents CSRF(Cross Site Request Forgery)
 * RESTful
 * Provides JSON endpoints
 * About page is a responsive portfolio page of the author, source code is available at - https://github.com/ahmfrz/Portfolio-Site/
 * etc
 
## Installation steps
 Please follow the steps below:
 
### Pre-requisites:
 * Python 2.7 - https://www.python.org/downloads/
 * Any text editor for editing the code(Sublime text preferred - https://www.sublimetext.com/download)
 * Oracle Virtual Box - https://www.virtualbox.org/wiki/Downloads
 * Vagrant - https://www.vagrantup.com/downloads.html
 * Vagrant Configuration - https://github.com/udacity/fullstack-nanodegree-vm
 
### Steps
 1. Download/ Fork(Find steps for forking in 'How to Contribute' section) this repository in /vagrant/catalog directory
 2. Open Git Bash or your favorite command line tool and run following commands:
      vagrant up
      vagrant ssh
 3. Navigate to /vagrant/catalog directory
 4. Run following command in virtual machine:
      python app.py
 4. Open Chrome(Or any other browser) and navigate to 'http://localhost:8000/'
 5. Verify that Catalog webpage is displayed
 
## Resources

* [Bootstrap documentation](http://getbootstrap.com/) - Helpful documentation.
* [Github flavored markdown reference](https://help.github.com/categories/writing-on-github/) - Github own documentation about documentation
* [Writing ReadMes](https://github.com/udacity/ud777-writing-readmes/edit/master/README.md) - Nice guide for building read mes
* [SQLALchemy documentation](http://docs.sqlalchemy.org/en/latest/) - Open source ORM
* [Google OAuth2](https://developers.google.com/) - OAuth2
* [Facebook OAuth2](https://developers.facebook.com/) - OAuth2
* [Github OAuth2](https://developer.github.com/) - OAuth2

## How to Contribute

Find any bugs? Have another feature you think should be included? Contributions are welcome!

First, fork this repository.

![Fork Icon](fork-icon.png)

Next, clone this repository to your desktop to make changes.

```sh
$ git clone {YOUR_REPOSITORY_CLONE_URL}
$ cd folder
```

Once you've pushed changes to your local repository, you can issue a pull request by clicking on the green pull request icon.

![Pull Request Icon](pull-request-icon.png)

## License

The contents of this repository are covered under the [MIT License](LICENSE).
