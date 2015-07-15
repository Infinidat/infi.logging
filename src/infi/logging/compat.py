import logbook


def redirect_python_logging_to_logbook():
    from logbook.compat import redirect_logging
    redirect_logging()
