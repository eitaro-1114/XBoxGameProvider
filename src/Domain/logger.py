from logging import DEBUG, Logger, StreamHandler, getLogger


def get_logger(name: str) -> Logger:
    logger = getLogger(name)
    logger.setLevel(DEBUG)

    handler = StreamHandler()
    handler.setLevel(DEBUG)

    logger.addHandler(handler)

    return logger
