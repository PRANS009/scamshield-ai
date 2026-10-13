from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine, String, Text, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

class SavedReport(Base):
    __tablename__ = 'risk_reports'
    id: Mapped[str] = mapped_column(String(36),primary_key=True)
    owner: Mapped[str] = mapped_column(String(64),index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)

class EvidenceRecord(Base):
    __tablename__ = 'evidence_sources'
    id: Mapped[str] = mapped_column(String(36),primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey('risk_reports.id'),index=True)
    payload: Mapped[str] = mapped_column(Text)

class Application(Base):
    __tablename__ = 'application_tracking'
    id: Mapped[str] = mapped_column(String(36),primary_key=True)
    owner: Mapped[str] = mapped_column(String(64),index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)

class Snapshot(Base):
    __tablename__ = 'opportunity_snapshots'
    id: Mapped[str] = mapped_column(String(36),primary_key=True)
    application_id: Mapped[str] = mapped_column(ForeignKey('application_tracking.id'),index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    text: Mapped[str] = mapped_column(Text)

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
Session = sessionmaker(engine)

def now():
    return datetime.now(timezone.utc).isoformat()

def new_id():
    return str(uuid4())

def init_db():
    Base.metadata.create_all(engine)
