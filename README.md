# saas-api-boilerplate
Boilerplate setup for SaaS [JSONAPI](http://jsonapi.org/format/) in Python using Flask &amp; SQLAlchemy

## Development Setup

Document how I like to setup a Python API Project.

### Sublime Text Project

[The .sublime-project file should be checked into version control.](https://www.sublimetext.com/docs/3/projects.html) Add `*.sublime-workspace` to `.gitignore`.

Exclude some cache files from the project by adding `"folder_exclude_patterns": [".cache", "__pycache__"]`

### Create a Virtual Environment

pyenv uses shim scripts to select the correct virtualenv for a file based on it's path. This allows tools like Sublime Text to run pylint and find the correct libraries.

```
cd $PROJECT_DIR
brew install pyenv pyenv-virtualenv
CFLAGS="-I$(brew --prefix openssl)/include" LDFLAGS="-L$(brew --prefix openssl)/lib" pyenv install 3.6.3
pyenv virtualenv 3.6.3 v$PROJECT_CODE
pyenv local v$PROJECT_CODE
pip install --upgrade pip setuptools
```

Errors like `zipimport.ZipImportError: can't decompress data; zlib not available` can be resolved by installing xcode tools: `xcode-select --install`

### Requirements Files

The default `requirements.txt` file created by `pip freeze` is used to install the dependencies for the deployed code.

The `requirements.raw` file tracks and documents the top level dependencies for the project. (Flask, SQLAlchemy, etc.)

After `pip install -r requirements.raw` be sure to `pip freeze > requirements.txt` before installing the development dependencies in `requirements.dev`.

The `requirements.dev` file tracks and documents the development environment dependencies for the project that should not be installed on deploy. (pylint, pytest, etc.)

#### Install Requirements

Install the same requirements as used on deploy:

```
pip install -r requirements.txt # deploy dependencies
pip install -r requirements.dev # dev dependencies
```

For PostgreSQL:
```
brew install postgresql
sed -i '' -e "s/timezone = 'US\/Eastern'/timezone = 'UTC'/" /usr/local//var/postgres/postgresql.conf
pg_ctl --pgdata=/usr/local/var/postgres --log=/dev/null start # start postgresql
createuser api --createdb
createdb $PROJECT_dev -U api
```

For MySQL:
```
brew install mariadb
echo -e "[mysqld]\ndefault-time-zone='+00:00'" > /usr/local/etc/my.cnf.d/default-time-zone.cnf
mysql.server start
mysql -u root -e 'CREATE DATABASE `'$PROJECT'_dev` /*!40100 DEFAULT CHARACTER SET utf8 */'
```

## Directory Structure

* common
  * Module catchall for shared code (log and utilities)
* models
  * Resource models, don't use flask-sqlalchemy so the models can be used by scripts outside of flask context.
