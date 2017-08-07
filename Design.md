## Design Decisions

General design desisions made for this project.

### Database Sessions

Don't use flask-sqlalchemy because that would require a flask context to use the models. Separating these out will allow for non-api (scripts, other tools) to use the models. Instead we will have a models.db module that will manage the sessions, and use a Flask teardown callback to cleanup the sessions manually.

### Separate Profiles from Logins

1. Track password history for password reuse rules.
2. Remove login without losing Profile data.
3. Have Profiles without Logins for initial setup before notifying users, or for people that won't ever login.

### Access Tokens

1. Track Login sessions.
2. Create Login Tokens for Admins without knowing password.
3. Login session timeouts.

### Multi-tenancy Database

1. Easier cross customer analysis.
2. Less infrastructure.
3. Allow Logins to access multiple tenant's models.

### Role Based Access Control

More flexible for differing access cases.

### Response Compression

CloudFront includes [compression](https://aws.amazon.com/blogs/aws/new-gzip-compression-support-for-amazon-cloudfront/), which is a preferred solution for this requirement. Other Cloud [providers](https://cloud.google.com/appengine/kb/#compression) hopefully offer something similar.

Other options include:

* https://thejimmyg.github.io/pylonsbook/en/1.1/the-web-server-gateway-interface-wsgi.html#altering-the-response
* https://github.com/libwilliam/flask-compress
