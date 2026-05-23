import logging
from BuildScheduler.Scheduler.utils.state import logfile_location

logger = logging.getLogger(__name__)
logging.basicConfig(filename=logfile_location, encoding='utf-8', level=logging.DEBUG)


async def vire_logger(log_type: str, obj:str, *args)-> None: #cfn is a shorthand to 'custom function'
    """log_type levels: [info | warn | error | critical | exit]"""
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
            logger.warning("[cfn_log] Log type '%s' is not supported by cfn_log.", l_type)
    except Exception as e:
        logger.error("[cfn_log] An error occoured in the logging function. (%s)", e, exc_info=True)
