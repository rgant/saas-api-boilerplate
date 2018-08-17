# saas-api-boilerplate

Boilerplate setup for SaaS [JSONAPI](http://jsonapi.org/format/) in Python using
Flask & SQLAlchemy

## Development Setup

Document how I like to setup a Python API Project.

### Sublime Text Project

[The .sublime-project file should be checked into version control.](https://www.sublimetext.com/docs/3/projects.html)
Add `*.sublime-workspace` to `.gitignore`.

Exclude some cache files from the project by excluding some folder from the sublime-project
settings:
`"folder_exclude_patterns": [".cache", ".mypy_cache", ".pytest_cache", "__pycache__"]`

### Create a Virtual Environment

SublimeLinter has integrated support for pipenv now so we can fully use pipenv's
virtualenv creation.

```bash
brew install pyenv pipenv
cd "${PROJECT_DIR}"
pipenv --three
```

Errors like `zipimport.ZipImportError: can't decompress data; zlib not available`
can be resolved by installing xcode tools: `xcode-select --install`

### Dependencies

Using `pipenv` the project and development dependencies are tracked in `Pipfile`
and `Pipfile.lock`. The requirements files for pip have been migrated and moved.

Since the Pipfile loses comments on each `pipenv install` this list documents the
reason for certain dependencies:

1. bcrypt # Password Hashing for Login
2. \# Flask-REST-JSONAPI # JSONAPI in Flask (seems abandoned or just slow to develop,
   we can do better.)
3. Flask # Flask web server
4. future # Python3 Compatibility (import builtins)
5. gunicorn # Server for deployed app
6. marshmallow-jsonapi # Handle the JSONAPI Envelope for API Schemas
7. marshmallow-sqlalchemy # Map DB Models to API Schemas
8. mypy # Not a development requirement because we may need to import from mypy
9. psycopg2 # PostgreSQL library
10. PyMySQL # PDO for MySQL appropriate for Google Cloud SQL DB
11. SQLAlchemy # ORM
12. SQLAlchemy-Continuum # Audit log/versioning

#### Install Requirements

Install the same requirements as locked by pipenv: `pipenv sync --dev`

For PostgreSQL:

```bash
brew install postgresql
sed -i '' -e "s/timezone = 'US\\/Eastern'/timezone = 'UTC'/" /usr/local//var/postgres/postgresql.conf
pg_ctl --pgdata=/usr/local/var/postgres --log=/dev/null start # start postgresql
createuser api --createdb
createdb "${PROJECT_NAME}_dev" -U api
```

For MySQL:

```bash
brew install mariadb
echo -e "[mysqld]\\ndefault-time-zone='+00:00'" > /usr/local/etc/my.cnf.d/default-time-zone.cnf
mysql.server start
mysql -u root -e 'CREATE DATABASE `'"${PROJECT_NAME}_dev"'` /*!40100 DEFAULT CHARACTER SET utf8 */'
```

##### Update Requirements

```bash
pipenv update --outdated --dev # Look for updates allowed by Pipfile
pipenv update --dev # Actually install updates to dependencies
```

#### Code Checks

Because we are using pipenv all the python commands need to be run using
`pipenv run`. The three commands below are configured in the Pipfile scripts.

Linting the code: `pipenv run lint`

Type checking: `pipenv run mypy`

Run tests: `pipenv run test`

I don't like `pipenv shell` and I haven't setup an [automatic activation of the
virtualenv](https://github.com/pypa/pipenv/wiki/Run-pipenv-shell-automatically)
so for now we need to remember to use `pipenv run`.

## Directory Structure

* common
  * Module catchall for shared code (log and utilities)
* models
  * Resource models, don't use flask-sqlalchemy so the models can be used by scripts
    outside of flask context.

## References & Examples

* [Our Approach to Resource Governance and Role-Based Access Control (RBAC)](https://cloudify.co/2018/04/04/our-approach-to-resource-governance-and-role-based-access-control-rbac/)
