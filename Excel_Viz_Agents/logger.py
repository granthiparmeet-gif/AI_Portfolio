import logging

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(h)
    return logger