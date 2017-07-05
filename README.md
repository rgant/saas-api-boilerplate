# saas-api-boilerplate
Boilerplate setup for SaaS JSONAPI in Python using Flask &amp; SQLAlchemy

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
pyenv install 3.6.1
pyenv virtualenv 3.6.1 v$PROJECT_CODE
pyenv local v$PROJECT_CODE
pip install --upgrade pip setuptools
```

### Requirements Files

The default `requirements.txt` file created by `pip freeze` is used to install the dependencies for the deployed code.

The `requirements.raw` file tracks and documents the top level dependencies for the project. (Flask, SQLAlchemy, etc.)

After `pip install -r requirements.raw` be sure to `pip freeze > requirements.txt` before installing the development dependencies in `requirements.dev`.

The `requirements.dev` file tracks and documents the development environment dependencies for the project that should not be installed on deploy. (pylint, pytest, etc.)
