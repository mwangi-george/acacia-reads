from enum import Enum


class BookCategory(str, Enum):
    """An enumeration for various book categories"""

    # --- Fiction Categories ---
    FICTION = 'FICTION'
    MYSTERY = 'MYSTERY'
    FANTASY = 'FANTASY'
    SCIENCE_FICTION = 'SCIENCE_FICTION'
    ROMANCE = 'ROMANCE'
    THRILLER = 'THRILLER'
    HORROR = 'HORROR'
    ADVENTURE = 'ADVENTURE'
    HISTORICAL_FICTION = 'HISTORICAL_FICTION'

    # --- Non-Fiction Categories ---
    NON_FICTION = 'NON_FICTION'
    BIOGRAPHY = 'BIOGRAPHY'
    AUTOBIOGRAPHY = 'AUTOBIOGRAPHY'
    HISTORY = 'HISTORY'
    SELF_HELP = 'SELF_HELP'
    BUSINESS = 'BUSINESS'
    COOKBOOKS = 'COOKBOOKS'
    TRAVEL = 'TRAVEL'
    SCIENCE = 'SCIENCE'

    # --- Other Categories ---
    POETRY = 'POETRY'
    CHILDREN = 'CHILDREN'
    GRAPHIC_NOVEL = 'GRAPHIC_NOVEL'
    ACADEMIC = 'ACADEMIC'
    PHILOSOPHY = 'PHILOSOPHY'


class OrderStatus(str, Enum):
    """An enumeration for various book order statuses"""
    PENDING = 'PENDING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'


class PaymentStatus(str, Enum):
    """An enumeration for various payment statuses"""
    PENDING = 'PENDING'
    PAID = 'PAID'
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'


class UserRole(str, Enum):
    """An enumeration for various user roles"""
    ADMIN = 'ADMIN'
    USER = 'USER'