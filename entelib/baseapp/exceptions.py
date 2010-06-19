#-*- coding=utf-8 -*-


# our base exception
class EntelibError(Exception):
    pass


class ReservationError(EntelibError):
    pass


class CancelReservationError(ReservationError):
    pass
