import logging 

def setup_logging():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    app_logger=logging.getLogger("GrocerEase") 
    app_logger.setLevel(logging.INFO) 

    app_file_handler=logging.FileHandler("logger/logs.log") 
    app_file_handler.setLevel(logging.INFO) 
    app_file_handler.setFormatter(formatter) 

    if not app_logger.handlers: 
        app_logger.addHandler(app_file_handler) 
 
    app_logger.propagate=False 