from sqlalchemy.ext.declarative import declarative_base
from .users import User
from .business import Business
from .menu import Category, Product, ProductOption, ProductCategory
from .orders import Order, OrderItem, OrderItemOption
from .payments import Payment, Transaction
from .delivery import DeliveryZone, DeliveryDistance
from .bonus import BonusTransaction, Referral
from .notification import Notification

# Create a base class for all models
# Base = declarative_base()