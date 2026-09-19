class OrderNotFoundError(Exception):
    pass

class OrderCannotBeCancelledError(Exception):
    pass

class OrderCannotBeReturnedError(Exception):
    pass

class ReturnAlreadyRequestedError(Exception):
    pass

class AlreadyCancelledOrderError(Exception):
    pass