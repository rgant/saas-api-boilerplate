# saas-api-boilerplate
Boilerplate setup for SaaS [JSONAPI](http://jsonapi.org/format/) in Python using Flask &amp; SQLAlchemy

## Development Setup

Document how I like to setup a Python API Project.

### Sublime Text Project

[The .sublime-project file should be checked into version control.](https://www.sublimetext.com/docs/3/projects.html) Add `*.sublime-workspace` to `.gitignore`.

Exclude some cache files from the project by adding `"folder_exclude_patterns": [".cache", "__pycache__"]`

### Create a Virtual Environment

pyenv uses shim scripts to select the correct virtualenv for a file based on it's path. This allows tools like Sublime Text to run pylint and find the correct libraries.

I don't really like `pipenv shell` and how that makes it complicated for SublimeText to figure out what python virtualenv to use. So I won't be allowing `pipenv` to create virtualenvs. Luckily it will use the current one if one is active.

```
cd $PROJECT_DIR
brew install pyenv pyenv-virtualenv pipenv
CFLAGS="-I$(brew --prefix openssl)/include" LDFLAGS="-L$(brew --prefix openssl)/lib" pyenv install 3.6.3
pyenv virtualenv 3.6.3 v$PROJECT_CODE
pyenv local v$PROJECT_CODE
pip install --upgrade pip setuptools
```

Errors like `zipimport.ZipImportError: can't decompress data; zlib not available` can be resolved by installing xcode tools: `xcode-select --install`

### Dependencies

Using `pipenv` the project and development dependencies are tracked in `Pipfile` and `Pipfile.lock`. The requirements files for pip have been migrated and moved.

Since the Pipfile loses comments on each `pipenv install` this list documents the reason for certain dependencies:

1. bcrypt # Password Hashing for Login
2. \# Flask-REST-JSONAPI # JSONAPI in Flask (seems abandoned or just slow to develop, we can do better.)
3. Flask # Flask web server
4. future # Python3 Compatibility (import builtins)
5. gunicorn # Server for deployed app
6. marshmallow-jsonapi # Handle the JSONAPI Envelope for API Schemas
7. marshmallow-sqlalchemy # Map DB Models to API Schemas
8. psycopg2 # PostgreSQL library
9. PyMySQL # PDO for MySQL appropriate for Google Cloud SQL DB
10. SQLAlchemy # ORM
11. SQLAlchemy-Continuum # Audit log/versioning

If you add new dependencies, you will need to inform pyenv: `pyenv rehash` will update which packages are installed in the virtualenv.

#### Install Requirements

Install the same requirements as used on deploy: `pipenv install --dev`

And then you need to create the shims for pyenv that you installed: `pyenv rehash`

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

##### Update Requirements

```
pipenv update --outdated --dev # Look for updates allowed by Pipfile
pipenv update --dev # Actually install updates to dependencies
pyenv rehash # Inform pyenv of modules installed by pipenv
```

## Directory Structure

* common
  * Module catchall for shared code (log and utilities)
* models
  * Resource models, don't use flask-sqlalchemy so the models can be used by scripts outside of flask context.
