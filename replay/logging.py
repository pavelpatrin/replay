from logging.config import dictConfig


def configure(level):
    dictConfig({
        'formatters': {
            'detailed': {
                'format': '[%(asctime)s %(levelname)s %(name)s] %(message)s',
            },
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed',
                'level': level,
            }
        },
        'loggers': {
            'replay': {
                'handlers': ['stream'],
                'propagate': False,
                'level': level,
            },
        },
        'root': {
            'handlers': ['stream'],
            'level': 'INFO',
        },
        'disable_existing_loggers': False,
        'version': 1,
    })
