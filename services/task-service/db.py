from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

task_labels = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)


class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    tasks = relationship("Task", back_populates="list")

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    labels = relationship("Label", secondary=task_labels, backref="tasks")
    list = relationship("List", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "list": self.list.name if self.list else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "labels": [l.name for l in self.labels],
        }


def init_db(database_url: str, retries=15, delay=2):
    import time
    engine = create_engine(database_url)
    for attempt in range(retries):
        try:
            Base.metadata.create_all(engine)
            break
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not session.query(List).filter_by(name="Inbox").first():
        session.add(List(name="Inbox"))
        session.commit()
    session.close()
    return Session
