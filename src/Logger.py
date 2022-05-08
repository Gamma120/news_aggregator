import logging

    
def set_logger(logger_name, log_file, mode='a', level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    fileHandler = logging.FileHandler(log_file, mode=mode)
    
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)
    l.setLevel(level)
    l.addHandler(fileHandler)