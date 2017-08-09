## Combining marshmallow-jsonapi and marshmallow-sqlalchmey

[marshmallow-sqlalchemy](https://github.com/marshmallow-code/marshmallow-sqlalchemy) includes a ModelConverter that will map SQLAlchemy types to [Marshmallow](https://github.com/marshmallow-code/marshmallow) field types. However it will map relations to a marshmallow-sqlalchemy Relation which on serialization will be output to the data in the Relation. In [marshmallow-jsonapi](https://github.com/marshmallow-code/marshmallow-jsonapi) we would rather have those SQLAlchemy relations be converted into Relationship fields. This document describes how to arrange for that conversion with a minimum of duplication of efforts.

### Default Assumptions

Producing this conversion automatically relies on several assumptions and automatic calculations to configure the relationships. For the purposes of this documentation "model" shall refer to an SQLAlchemy ORM declarative base derived class, and "schema" shall refer to a marshmallow Schema derived class.

1. The class name for a schema for a model should be the `model.__name__ + 'Schema'`.
2. The marshmallow-jsonapi `type_` option for the schema will be automatically set to the `model.__name__`.
3. The marshmallow-jsonapi `self_url` and `self_url_many` options for the schema will be automatically set to the `type_` value plus the `id` field.
4. The marshmallow-jsonapi Relationship `related_url` and `self_url` options will be set to the Model relation property key suffixed to the schema's `self_url`.
5. The Relationship field `self_url_kwargs` and `related_url_kwargs` options will be the same as the schema's `self_url_kwargs`.
6. We will introduce a new schema option `listable` that will identify if the Model+Schema endpoint will support a list (many) operations.

Just for fun we will also dasherize the field names, `type_`, and relation property keys to follow [JSONAPI spec recommendations](http://jsonapi.org/recommendations/#naming).

### Example Models and Schema

```python
import sqlalchemy as sa
import sqlalchemy.orm as saorm

from models import bases
import ourmarshmallow


class Articles(bases.BaseModel):
    """ Articles have authors and comments. """
    title = sa.Column(sa.String(50), nullable=False)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('authors.id'), nullable=False)

    author = saorm.relationship('Authors', back_populates='articles')
    comments = saorm.relationship('Comments', back_populates='article')

class Authors(bases.BaseModel):
    """ Authors of comments or articles. """
    full_name = sa.Column(sa.String(50), nullable=False)

    articles = saorm.relationship('Articles', back_populates='author')
    comments = saorm.relationship('Comments', back_populates='author')


class Comments(bases.BaseModel):
    """ Comments to an Article by an Author """
    message = sa.Column(sa.Text, nullable=False)

    article_id = sa.Column(sa.Integer, sa.ForeignKey('articles.id'), nullable=False)
    author_id = sa.Column(sa.Integer, sa.ForeignKey('authors.id'), nullable=False)

    article = saorm.relationship('Articles', back_populates='comments')
    author = saorm.relationship('Authors', back_populates='comments')


class ArticlesSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema for Articles """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Articles


class AuthorsSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema for Authors """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Authors


class CommentsSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema for Comments """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Comments


# Create a bunch of data and put some Articles into a list, then:
schema = ArticlesSchema(many=True, include_data=('comments.author', 'author.comments'))
data = schema.dump(articles).data
```

### Customized Relationship Field

In [ourmarshmallow.fields](fields.py) the Relationship class customizations:

* `parent_self_url` is the `self_url` option for the schema containing the Relationship field.
  * Example: `ArticlesSchema.opts.self_url == '/articles/{id}'`
* `relationship_name` is the attribute name for the relationship on Model.
  * Example: `Articles.author`

These values, plus `self_url_kwargs` are set automatically by the converter when converting the model to a schema. When all three are set on initialization of the Relationship object then:

* The `Relationship.self_url` is set to `Relationship.parent_self_url + '/relationships/' + Relationship.relationship_name`.
  * Example: `/articles/{id}/relationships/author`
* The `Relationship.related_url` is set to `Relationship.parent_self_url + Relationship.relationship_name`.
  * Example: `/articles/{id}/author`
* The `Relationship.related_url_kwargs` is set to `Relationship.self_url_kwargs`
  * Example: `related_url_kwargs = self_url_kwargs = {'id': '<id>'}`

### Customized ModelConverter

In [ourmarshmallow.convert](convert.py) the ModelConverter class customizations:

* All `DIRECTION_MAPPING` keys are set to `False` values so that to many relations aren't wrapped in a List. This is a hack that isn't very pretty.
* `_get_field_class_for_property` checks for the SQLAlchemy property to have a direction attribute, if so it returns our customized Relationship class. Otherwise it returns the super() method.
* `_add_relationship_kwargs` add the additional kwargs for our Relationship class:
  * `Relationship(schema)` parameter is set to `model.__name__ + 'Schema'`.
    * This is necessary because all the Models for type_ aren't necessarily created when the Relationship is initialized.
  * `Relationship(many)` parameter is set to the SQLAlchemy `property.uselist`.
    * This is necessary because we broke the `DIRECTION_MAPPING` attribute and it's how the super() code already checks things.
  * `Relationship(type_)` parameter is set to the (dasherized) version of `model.__name__`.
    * Example: `camel_to_kebab_case(CamelCase.__name__) == 'camel-case'`
  * `Relationship(relationship_name)` parameter is set to the (dasherized) version of the attribute name for the SQLAlchemy relation.
    * Example: `kwargs['relationship_name'] == dasherize(Comments.author.prop.key)`
  * `Relationship(parent_self_url)` parameter is set to the `self_url` of the `schema_cls` for the converter.
    * Example: `kwargs['parent_self_url'] = CommentsSchema.opts.self_url`
  * `Relationship(self_url_kwargs)` parameter is set to the `self_url_kwargs` of the `schema_cls` for the converter.
    * Example: `kwargs['self_url_kwargs'] = CommentsSchema.opts.self_url_kwargs`

### Customized Schema

In [ourmarshmallow.schema](schema.py) the Schema is customized for more than just merging marshmallow-jsonapi and marshmallow-sqlalchemy. The customizations are:

* Re-define the `id` field to be an `Integer(as_string=True)` to better implement JSONAPI spec where identifiers must be strings.
* Re-define the `modified_at` DateTime column to use our customized MetaData field type.
  * Ideally all read only columns would be JSONAPI metadata but the hooks for this in the parent marshmallow_jsonapi.Schema aren't available for easy conversion using our ModelConverter.
* On `Schema.__init__` set the marshmallow-sqlalchemy Schema session to the current session. This makes sure that whenever a Schema class is instantiated that we have the current SQLAlchemy session.
* Add an extra check to `unwrap_item` that requires the `id` field when the schema has an existing model instance (update/patch operations).
* Add a custom validation to the `id` field to check for matching identifier values when the schema has an existing model instance (update/patch operations).
  * Raises a custom Exception `MismatchIdError` based on `marhsmallow_jsonapi.exceptions.IncorrectTypeError` so that servers can respond with a 409 Conflict in accordance with the JSONAPI spec.
* Use a custom SCHEMA_OPTS class to customized the options for our schemas.
  * Add a new `listable` option to our Schemas. When this is `True` then the api should allow for a GET method to return a list.
  * Always set `strict` option to `True` for our schemas. (Pending marshmallow-code/marshmallow#377 resolution.)
  * If the marshmallow-sqlalchmey `model` option for the schema is set then:
    * Set the `type_` option to the (dasherized) `model.__name__`.
    * Set `self_url` option to the `'/' + type_ + '/{id}'`.
    * Set `self_url_kwargs` option to `{'id': '<id>'}`.
    * Set `self_url_many` to `'/' + type_`.
      * This is used for creation of new models, in addition to potentially listing them if `listable` is `True`.
  * Sets the marshmallow-sqlalchemy `model_converter` option to use our customized ModelConverter.
  * Sets the marshmallow-jsonapi `inflect` option to use a dasherize function.
