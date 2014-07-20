import logbook


def redirect_python_logging_to_logbook():
    """
    Safely redirects Python's stdandard library logging to logbook. Unlike logbook.compat.redirect_logging,
    this method can be called multiple times in the same process or logbook context.
    """
    # When we run nose tests we want to the opposite - redirect logbook to logging so nose will capture it.
    # So we shound't redirect back in this case otherwise we'll cause an infinite recursion loop.
    from logbook.compat import redirect_logging, LoggingHandler
    if not any(isinstance(obj, LoggingHandler) for obj in logbook.default_handler.stack_manager.iter_context_objects()):
        redirect_logging()
