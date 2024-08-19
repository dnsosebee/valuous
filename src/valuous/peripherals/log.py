import logging


def init_logger():

    # Create a custom logger
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('app.log')

    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)

    # Create formatters and add them to handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)
