# docker-sentry-ldap

## History

The work here is based on [slafs sentry repo](https://github.com/slafs/sentry-docker) and [banno](https://github.com/Banno/getsentry-ldap-auth) this `Dockerfile` is an extension of the [sentry official docker image](https://hub.docker.com/_/sentry/) so, any `ENVIRONMENT` documented there you can use here.

I guess that [slafs](https://github.com/slafs) stopped his word after Sentry releases their official Docker image, but for some reason, the image do not support LDAP stuff so we merged both and make it work.

Update 2019-08: Sentry released the 9 version with better customization support from the `-ondemand` we are now using this image as a source for ours. 

### Notes on version 9.1

Unfortunately `sentry run web` don't support the parameter `-b 0:$PORT0` where $PORT0 is the variable that your docker orchestrator fill with the currently available port to map, the official conf only support the `9000` port.

So we create a env var called `$PORT0` that you can pass your alternative port, the default is `9000` but if you use Kubernetes or other orchestrators you probably need to use `$PORT0` env 

## Example environment configuration

Environment variable name | Value
---------------------------------|-------------------------
LDAP_BIND_DN                     | uid=sentry,ou=Systems,dc=server,dc=com
LDAP_BIND_PASSWORD               | feijoada
LDAP_GROUP_TYPE                  | groupOfUniqueNames
LDAP_MAP_FIRST_NAME              | cn
LDAP_SERVER                      | ldaps://ldap.server.com:636
LDAP_USER_DN                     | ou=Employees,dc=company,dc=com
LDAP_USER_FILTER                 | =(&(objectClass=inetOrgPerson)(mail=%(user)s))
LDAP_DEFAULT_SENTRY_ORGANIZATION | Locaweb
SENTRY_DB_NAME                   | sentry
SENTRY_DB_PASSWORD               | dbpasswd 
SENTRY_DB_USER                   | sentry
SENTRY_EMAIL_HOST                | email.relay.com
SENTRY_EMAIL_PORT                | 25
SENTRY_MEMCACHED_HOST            | memcached_farm.server.com
SENTRY_MEMCACHED_PORT            | 11211
SENTRY_POSTGRES_HOST             | postgres.server.com 
SENTRY_REDIS_HOST                | redis.server.com 
SENTRY_REDIS_PORT                | 11042
SENTRY_SECRET_KEY                | secret_sentry_key_42 
SENTRY_SERVER_EMAIL              | noreply@server.com
SENTRY_USE_LDAP                  | True

## Available environment variables

Refer to [sentry documentation](https://docs.getsentry.com/server/config/),
[django documentation](https://docs.djangoproject.com/en/1.6/ref/settings/),
[celery documentation](http://docs.celeryproject.org/en/latest/)
and [django-auth-ldap documentation](https://pythonhosted.org/django-auth-ldap/reference.html)
for the meaning of each setting.

Environment variable name       | Django/Sentry setting                         | Type | Default value                                         | Description
---------------------------------|-----------------------------------------------|------|-------------------------------------------------------|------------------------------------------------------------------------
SENTRY_USE_LDAP                  |                                               | bool | False                                                 | if set to ``False`` all other LDAP settings are discarded
LDAP_SERVER                      | AUTH_LDAP_SERVER_URI                          |      | ``ldap://localhost``                                  | Example: ``ldaps://ldap.locaweb.com:639`` 
LDAP_BIND_DN                     | AUTH_LDAP_BIND_DN                             |      | ''                                                    | The user used to login at ldap, normally this is a system user example:  uid=sentry,ou=Systems,dc=locaweb,dc=com
LDAP_BIND_PASSWORD               | AUTH_LDAP_BIND_PASSWORD                       |      | ''                                                    | The password of the user 
LDAP_USER_DN                     | AUTH_LDAP_USER_SEARCH*                        |      | **REQUIRED!** if you want to use LDAP auth            | first argument of LDAPSearch (base_dn) when searching for users
LDAP_USER_FILTER                 | AUTH_LDAP_USER_SEARCH*                        |      | ``(&(objectClass=inetOrgPerson)(cn=%(user)s))``       | third argument of LDAPSearch (filterstr) when searching for users
LDAP_GROUP_DN                    | AUTH_LDAP_GROUP_SEARCH*                       |      | ''                                                    | first argument of LDAPSearch (base_dn) when searching for groups
LDAP_GROUP_FILTER                | AUTH_LDAP_GROUP_SEARCH*                       |      | ``(objectClass=groupOfUniqueNames)``                  | third argument of LDAPSearch (filterstr) when searching for groups
LDAP_GROUP_TYPE                  | AUTH_LDAP_GROUP_TYPE*                         |      | ''                                                    | if set to 'groupOfUniqueNames' then ``AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType()``, if set to 'posixGroup' then ``AUTH_LDAP_GROUP_TYPE = PosixGroupType()``.
LDAP_DEFAULT_SENTRY_ORGANIZATION | AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION         |      | ``Locaweb``                                           | Name of the Sentry Default Organization
LDAP_REQUIRE_GROUP               | AUTH_LDAP_REQUIRE_GROUP                       |      | None                                                  |
LDAP_DENY_GROUP                  | AUTH_LDAP_DENY_GROUP                          |      | None                                                  |
LDAP_MAP_FULL_NAME               | AUTH_LDAP_USER_ATTR_MAP['first_name']         |      | ``cn``                                                | Please make sure that this property have the full name of the user 
LDAP_MAP_MAIL                    | AUTH_LDAP_USER_ATTR_MAP['email']              |      | ``mail``                                              |
LDAP_SENTRY_USER_FIELD           |                                               |      | ``mail``                                              | Which LDAP field will be used to create the Sentry username
LDAP_GROUP_ACTIVE                | AUTH_LDAP_USER_FLAGS_BY_GROUP['is_active']    |      | ''                                                    |
LDAP_GROUP_STAFF                 | AUTH_LDAP_USER_FLAGS_BY_GROUP['is_staff']     |      | ''                                                    |
LDAP_GROUP_SUPERUSER             | AUTH_LDAP_USER_FLAGS_BY_GROUP['is_superuser'] |      | ''                                                    |
LDAP_FIND_GROUP_PERMS            | AUTH_LDAP_FIND_GROUP_PERMS                    | bool | False                                                 |
LDAP_CACHE_GROUPS                | AUTH_LDAP_CACHE_GROUPS                        | bool | True                                                  |
LDAP_GROUP_CACHE_TIMEOUT         | AUTH_LDAP_GROUP_CACHE_TIMEOUT                 | int  | 3600                                                  |
LDAP_LOGLEVEL                    |                                               |      | ``DEBUG``                                             | django_auth_ldap logger level (other values: NOTSET (to disable), INFO, WARNING, ERROR or CRITICAL)


## Health-check

### Web

Just check the localhost:9000/_health/ of your container

### Workers

Use celery ping command:

```
$ sentry exec -c 'import celery, os; print(celery.task.control.inspect().ping().get("celery@{}".format(os.environ["HOSTNAME"]))["ok"])'
```

This will check if the celery daemon that is running on that host, is ok.

## Build

```
$ docker build -t "$DOCKER_REGISTRY_URL/sentry/sentry:9.1" .
```

