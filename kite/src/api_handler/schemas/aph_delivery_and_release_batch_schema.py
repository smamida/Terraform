# Import necessary SQLAlchemy components
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, MetaData

# Create a base class for declarative class definitions
Base = declarative_base()

# Create a MetaData instance to hold database metadata
metadata = MetaData()

class APHDeliveryReleaseBatchSchema(Base):
    """
    SQLAlchemy ORM model representing the 'aph_delivery_and_release_dashboard_vw' view in the database.

    This class defines the structure of the view, including all columns and their data types.
    It's used for database operations and ORM mappings, specifically for batch processing
    of APH (Apheresis) Delivery and Release data.

    The __table__ attribute is used instead of __tablename__ because this represents a view, not a table.
    """

    __table__ = Table(
        'aph_delivery_and_release_view',  # Name of the view
        metadata,
        Column('orderNumber', String(200), primary_key=True),  # Unique identifier for each order
        Column('kpid', String(200)),
        Column('coi', String(200)),
        Column('actualAphDelivery', DateTime),
        Column('commentsSiteEucom', String),
        Column('plannedAphDelivery', DateTime),
        Column('actualAphReleaseStart', DateTime),
        Column('commentsQcAph', String),
        Column('commentsRqoEme', String),
        Column('country', String(200)),
        Column('mfgOrganizationProd', String(250)),
        Column('actualAphReleaseEnd', DateTime),
        Column('actualAphDate', DateTime),
        Column('lotExpiry', DateTime),
        schema='public'                                     
    )

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        """
        Provides a string representation of the APHDeliveryReleaseBatchSchema instance.

        Returns:
            str: A string representation of the instance, showing the order number, KPID, and COI.
        """
        return f"<APHDeliveryReleaseBatchSchema(order_number={self.order_number}, kpid='{self.kpid}', coi='{self.coi}')>"
