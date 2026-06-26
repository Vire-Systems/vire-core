"""
Basic Vire logging setup.
"""

import logging

def sync_vire_logger(log_type: str, obj:str, *args)-> None:
    """log_type levels: [info | warn | error | critical | exit]"""
    logger = logging.getLogger()
    try:
        l_type = log_type.lower()
        if l_type == 'info':
            logger.info(obj, *args)
        elif l_type.lower() == 'warn':
            logger.warning(obj, *args)
        elif l_type == 'error':
            logger.error(obj, *args,exc_info=True ,stack_info=True)
        elif l_type == 'critical':
            logger.critical(obj, *args, stack_info=True, exc_info=True)
        elif l_type == 'exit':
            logger.critical(obj, *args)
        else:
            logger.warning("[vire_logger] Log type '%s' is not supported by cfn_log.", l_type)
    except Exception as e:
        logger.error("[vire_logger] An error occoured in the logging function. (%s)", e, exc_info=True)


async def vire_logger(log_type: str, obj:str, *args)-> None:
    """
    log_type levels: [info | warn | error | critical | exit]
    
    This is an async function with a synchronous function. The func itself does not block due to QueueHandler logging setup.
    check GC/logger/logger_setup.py for details.
    """
    try:
        sync_vire_logger(log_type, obj, *args)
    except Exception as e:
        logger = logging.getLogger()
        logger.error("[vire_logger] An error occoured in the async function wrapper. (%s)", e, exc_info=True)
