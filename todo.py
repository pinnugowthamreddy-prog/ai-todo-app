# -----------------------------------------
# DATABASE SCHEMA (SQLAlchemy)
# -----------------------------------------
class DBTask(Base):
    __tablename__ = "tasks" # The actual name of the table in SQL

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String, default="pending")

# This command tells SQLAlchemy to actually create the tables in the database!
Base.metadata.create_all(bind=engine)

# -----------------------------------------
# INTERNET DATA VALIDATION (Pydantic)
# -----------------------------------------
# We keep this from your old code!
class Task(BaseModel):
    title: str
    status: str = "pending"
    # Notice we removed 'id'. The SQL database will auto-generate IDs for us now!