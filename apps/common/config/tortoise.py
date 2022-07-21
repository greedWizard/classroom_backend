from . import config


TORTOISE_ORM = {
    'connections': {'default': config.DB_CONNECTION_STRING},
    'apps': {
        'models': {
            'models': [
                'aerich.models',
            ]
            + config.APP_MODULES['models'],
            'default_connection': 'default',
        },
    },
}
