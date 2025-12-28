from sqlalchemy.ext.declarative import declarative_base
from .users import User
from .business import Business, BusinessAdmin, BusinessImage, BusinessHours
from .cart import CartItem
from .menu import Category, Product, ProductOption, ProductCategory, ProductOptionGroup, ProductVariant
from .orders import Order, OrderItem, OrderItemOption, OrderType, OrderStatus
from .payments import Payment, Transaction, PaymentStatus, PaymentMethod
from .delivery import DeliveryZone, DeliveryDistance, DeliveryPerson, DeliverySettings, DeliveryCost
from .bonus import BonusTransaction, Referral, BonusTransactionStatus, BonusTransactionType, BonusRule
from .notification import Notification, NotificationType, NotificationStatus, NotificationChannel

# Create a base class for all models
Base = declarative_base()




