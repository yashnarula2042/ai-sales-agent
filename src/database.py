from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import enum

Base = declarative_base()

class LeadStatus(enum.Enum):
    PENDING = "pending"
    AI_GENERATED = "ai_generated"
    SENT = "sent"
    FAILED = "failed"
    REPLIED = "replied"

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    company = Column(String)
    website = Column(String)
    status = Column(Enum(LeadStatus), default=LeadStatus.PENDING)
    personalized_email = Column(String)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sent_at = Column(DateTime)

engine = create_engine('sqlite:///data/leads.db')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session()
