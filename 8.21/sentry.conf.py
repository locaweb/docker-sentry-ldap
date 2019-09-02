# This file is just Python, with a touch of Django which means
# you can inherit and tweak settings to your hearts content.

# For Docker, the following environment variables are supported:
#  SENTRY_POSTGRES_HOST
#  SENTRY_POSTGRES_PORT
#  SENTRY_DB_NAME
#  SENTRY_DB_USER
#  SENTRY_DB_PASSWORD
#  SENTRY_RABBITMQ_HOST
#  SENTRY_RABBITMQ_USERNAME
#  SENTRY_RABBITMQ_PASSWORD
#  SENTRY_RABBITMQ_VHOST
#  SENTRY_REDIS_HOST
#  SENTRY_REDIS_PASSWORD
#  SENTRY_REDIS_PORT
#  SENTRY_REDIS_DB
#  SENTRY_MEMCACHED_HOST
#  SENTRY_MEMCACHED_PORT
#  SENTRY_FILESTORE_DIR
#  SENTRY_SERVER_EMAIL
#  SENTRY_EMAIL_HOST
#  SENTRY_EMAIL_PORT
#  SENTRY_EMAIL_USER
#  SENTRY_EMAIL_PASSWORD
#  SENTRY_EMAIL_USE_TLS
#  SENTRY_ENABLE_EMAIL_REPLIES
#  SENTRY_SMTP_HOSTNAME
#  SENTRY_MAILGUN_API_KEY
#  SENTRY_SINGLE_ORGANIZATION
#  SENTRY_SECRET_KEY
#  GITHUB_APP_ID
#  GITHUB_API_SECRET
#  BITBUCKET_CONSUMER_KEY
#  BITBUCKET_CONSUMER_SECRET
from sentry.conf.server import *  # NOQA

import os
import os.path

from decouple import config

CONF_ROOT = os.path.dirname(__file__)

postgres = env('SENTRY_POSTGRES_HOST') or (env('POSTGRES_PORT_5432_TCP_ADDR') and 'postgres')
if postgres:
    DATABASES = {
        'default': {
            'ENGINE': 'sentry.db.postgres',
            'NAME': (
                env('SENTRY_DB_NAME')
                or env('POSTGRES_ENV_POSTGRES_USER')
                or 'postgres'
            ),
            'USER': (
                env('SENTRY_DB_USER')
                or env('POSTGRES_ENV_POSTGRES_USER')
                or 'postgres'
            ),
            'PASSWORD': (
                env('SENTRY_DB_PASSWORD')
                or env('POSTGRES_ENV_POSTGRES_PASSWORD')
                or ''
            ),
            'HOST': postgres,
            'PORT': (
                env('SENTRY_POSTGRES_PORT')
                or ''
            ),
            'OPTIONS': {
                'autocommit': True,
            },
        },
    }

# You should not change this setting after your database has been created
# unless you have altered all schemas first
SENTRY_USE_BIG_INTS = True

# If you're expecting any kind of real traffic on Sentry, we highly recommend
# configuring the CACHES and Redis settings

###########
# General #
###########

# Instruct Sentry that this install intends to be run by a single organization
# and thus various UI optimizations should be enabled.
SENTRY_SINGLE_ORGANIZATION = env('SENTRY_SINGLE_ORGANIZATION', True)

#########
# Redis #
#########

# Generic Redis configuration used as defaults for various things including:
# Buffers, Quotas, TSDB

redis = env('SENTRY_REDIS_HOST') or (env('REDIS_PORT_6379_TCP_ADDR') and 'redis')
if not redis:
    raise Exception('Error: REDIS_PORT_6379_TCP_ADDR (or SENTRY_REDIS_HOST) is undefined, did you forget to `--link` a redis container?')

redis_password = env('SENTRY_REDIS_PASSWORD') or ''
redis_port = env('SENTRY_REDIS_PORT') or '6379'
redis_db = env('SENTRY_REDIS_DB') or '0'

SENTRY_OPTIONS.update({
    'redis.clusters': {
        'default': {
            'hosts': {
                0: {
                    'host': redis,
                    'password': redis_password,
                    'port': redis_port,
                    'db': redis_db,
                },
            },
        },
    },
})

#########
# Cache #
#########

# Sentry currently utilizes two separate mechanisms. While CACHES is not a
# requirement, it will optimize several high throughput patterns.

memcached = env('SENTRY_MEMCACHED_HOST') or (env('MEMCACHED_PORT_11211_TCP_ADDR') and 'memcached')
if memcached:
    memcached_port = (
        env('SENTRY_MEMCACHED_PORT')
        or '11211'
    )
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': [memcached + ':' + memcached_port],
            'TIMEOUT': 3600,
        }
    }

# A primary cache is required for things such as processing events
SENTRY_CACHE = 'sentry.cache.redis.RedisCache'

#########
# Queue #
#########

# See https://docs.getsentry.com/on-premise/server/queue/ for more
# information on configuring your queue broker and workers. Sentry relies
# on a Python framework called Celery to manage queues.

rabbitmq = env('SENTRY_RABBITMQ_HOST') or (env('RABBITMQ_PORT_5672_TCP_ADDR') and 'rabbitmq')

if rabbitmq:
    BROKER_URL = (
        'amqp://' + (
            env('SENTRY_RABBITMQ_USERNAME')
            or env('RABBITMQ_ENV_RABBITMQ_DEFAULT_USER')
            or 'guest'
        ) + ':' + (
            env('SENTRY_RABBITMQ_PASSWORD')
            or env('RABBITMQ_ENV_RABBITMQ_DEFAULT_PASS')
            or 'guest'
        ) + '@' + rabbitmq + '/' + (
            env('SENTRY_RABBITMQ_VHOST')
            or env('RABBITMQ_ENV_RABBITMQ_DEFAULT_VHOST')
            or '/'
        )
    )
else:
    BROKER_URL = 'redis://:' + redis_password + '@' + redis + ':' + redis_port + '/' + redis_db


###############
# Rate Limits #
###############

# Rate limits apply to notification handlers and are enforced per-project
# automatically.

SENTRY_RATELIMITER = 'sentry.ratelimits.redis.RedisRateLimiter'

##################
# Update Buffers #
##################

# Buffers (combined with queueing) act as an intermediate layer between the
# database and the storage API. They will greatly improve efficiency on large
# numbers of the same events being sent to the API in a short amount of time.
# (read: if you send any kind of real data to Sentry, you should enable buffers)

SENTRY_BUFFER = 'sentry.buffer.redis.RedisBuffer'

##########
# Quotas #
##########

# Quotas allow you to rate limit individual projects or the Sentry install as
# a whole.

SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

########
# TSDB #
########

# The TSDB is used for building charts as well as making things like per-rate
# alerts possible.

SENTRY_TSDB = 'sentry.tsdb.redis.RedisTSDB'

###########
# Digests #
###########

# The digest backend powers notification summaries.

SENTRY_DIGESTS = 'sentry.digests.backends.redis.RedisBackend'

################
# File storage #
################

# Uploaded media uses these `filestore` settings. The available
# backends are either `filesystem` or `s3`.

SENTRY_OPTIONS['filestore.backend'] = 'filesystem'
SENTRY_OPTIONS['filestore.options'] = {
    'location': env('SENTRY_FILESTORE_DIR'),
}

##############
# Web Server #
##############

# If you're using a reverse SSL proxy, you should enable the X-Forwarded-Proto
# header and set `SENTRY_USE_SSL=1`

if env('SENTRY_USE_SSL', False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    # 'workers': 3,  # the number of web workers
}

###############
# Mail Server #
###############


email = env('SENTRY_EMAIL_HOST') or (env('SMTP_PORT_25_TCP_ADDR') and 'smtp')
if email:
    SENTRY_OPTIONS['mail.backend'] = 'smtp'
    SENTRY_OPTIONS['mail.host'] = email
    SENTRY_OPTIONS['mail.password'] = env('SENTRY_EMAIL_PASSWORD') or ''
    SENTRY_OPTIONS['mail.username'] = env('SENTRY_EMAIL_USER') or ''
    SENTRY_OPTIONS['mail.port'] = int(env('SENTRY_EMAIL_PORT') or 25)
    SENTRY_OPTIONS['mail.use-tls'] = env('SENTRY_EMAIL_USE_TLS', False)
else:
    SENTRY_OPTIONS['mail.backend'] = 'dummy'

# The email address to send on behalf of
SENTRY_OPTIONS['mail.from'] = env('SENTRY_SERVER_EMAIL') or 'root@localhost'

# If you're using mailgun for inbound mail, set your API key and configure a
# route to forward to /api/hooks/mailgun/inbound/
SENTRY_OPTIONS['mail.mailgun-api-key'] = env('SENTRY_MAILGUN_API_KEY') or ''

# If you specify a MAILGUN_API_KEY, you definitely want EMAIL_REPLIES
if SENTRY_OPTIONS['mail.mailgun-api-key']:
    SENTRY_OPTIONS['mail.enable-replies'] = True
else:
    SENTRY_OPTIONS['mail.enable-replies'] = env('SENTRY_ENABLE_EMAIL_REPLIES', False)

if SENTRY_OPTIONS['mail.enable-replies']:
    SENTRY_OPTIONS['mail.reply-hostname'] = env('SENTRY_SMTP_HOSTNAME') or ''

# If this value ever becomes compromised, it's important to regenerate your
# SENTRY_SECRET_KEY. Changing this value will result in all current sessions
# being invalidated.
secret_key = env('SENTRY_SECRET_KEY')
if not secret_key:
    raise Exception('Error: SENTRY_SECRET_KEY is undefined, run `generate-secret-key` and set to -e SENTRY_SECRET_KEY')

if 'SENTRY_RUNNING_UWSGI' not in os.environ and len(secret_key) < 32:
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('!!                    CAUTION                       !!')
    print('!! Your SENTRY_SECRET_KEY is potentially insecure.  !!')
    print('!!    We recommend at least 32 characters long.     !!')
    print('!!     Regenerate with `generate-secret-key`.       !!')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

SENTRY_OPTIONS['system.secret-key'] = secret_key

if 'GITHUB_APP_ID' in os.environ:
    GITHUB_EXTENDED_PERMISSIONS = ['repo']
    GITHUB_APP_ID = env('GITHUB_APP_ID')
    GITHUB_API_SECRET = env('GITHUB_API_SECRET')

if 'BITBUCKET_CONSUMER_KEY' in os.environ:
    BITBUCKET_CONSUMER_KEY = env('BITBUCKET_CONSUMER_KEY')
    BITBUCKET_CONSUMER_SECRET = env('BITBUCKET_CONSUMER_SECRET')

####################
# LDAP settings ##
####################

SENTRY_USE_LDAP = config('SENTRY_USE_LDAP', default=False, cast=bool)

if SENTRY_USE_LDAP:
    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType, PosixGroupType, NestedGroupOfNamesType

    AUTH_LDAP_SERVER_URI = config('LDAP_SERVER', default='ldap://localhost')

    AUTH_LDAP_BIND_DN = config('LDAP_BIND_DN', default='')
    AUTH_LDAP_BIND_PASSWORD = config('LDAP_BIND_PASSWORD', default='')

    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        config('LDAP_USER_DN'),
        ldap.SCOPE_SUBTREE,
        config('LDAP_USER_FILTER', default='(&(objectClass=inetOrgPerson)(cn=%(user)s))')
    )

    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        config('LDAP_GROUP_DN', default=''),
        ldap.SCOPE_SUBTREE,
        config('LDAP_GROUP_FILTER', default='(objectClass=groupOfUniqueNames)')
    )

    if config('LDAP_GROUP_TYPE', default='') == 'groupOfUniqueNames':
        AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType()
    elif config('LDAP_GROUP_TYPE', default='') == 'posixGroup':
        AUTH_LDAP_GROUP_TYPE = PosixGroupType()
    elif config('LDAP_GROUP_TYPE', default='') == 'nestedGroupOfNames':
        AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType()

    AUTH_LDAP_REQUIRE_GROUP = config('LDAP_REQUIRE_GROUP', default=None)
    AUTH_LDAP_DENY_GROUP = config('LDAP_DENY_GROUP', default=None)

    AUTH_LDAP_USER_ATTR_MAP = {
        'username': config('LDAP_SENTRY_USER_FIELD', default='user'),
        'name': config('LDAP_MAP_FULL_NAME', default='cn'),
        'email': config('LDAP_MAP_MAIL', default='mail')
    }

    AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION = 'Locaweb'
    AUTH_LDAP_SENTRY_ORGANIZATION_ROLE_TYPE = 'member'
    AUTH_LDAP_FIND_GROUP_PERMS = False
    AUTH_LDAP_SENTRY_SUBSCRIBE_BY_DEFAULT = False

    ldap_is_active    = config('LDAP_GROUP_ACTIVE', default='')
    ldap_is_superuser = config('LDAP_GROUP_SUPERUSER', default='')
    ldap_is_staff     = config('LDAP_GROUP_STAFF', default='')

    if ldap_is_active or ldap_is_superuser or ldap_is_staff:
        AUTH_LDAP_USER_FLAGS_BY_GROUP = {
            'is_active': ldap_is_active,
            'is_superuser': ldap_is_superuser,
            'is_staff': ldap_is_staff,
        }

    AUTH_LDAP_FIND_GROUP_PERMS = config('LDAP_FIND_GROUP_PERMS', default=False, cast=bool)

    # Cache group memberships for an hour to minimize LDAP traffic
    AUTH_LDAP_CACHE_GROUPS = config('LDAP_CACHE_GROUPS', default=True, cast=bool)
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = config('LDAP_GROUP_CACHE_TIMEOUT', default=3600, cast=int)

    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + (
        'django_auth_ldap.backend.LDAPBackend',
    )



    # setup logging for django_auth_ldap
    import logging
    logger = logging.getLogger('django_auth_ldap')
    logger.addHandler(logging.StreamHandler())
    ldap_loglevel = getattr(logging, config('LDAP_LOGLEVEL', default='DEBUG'))
    logger.setLevel(ldap_loglevel)

