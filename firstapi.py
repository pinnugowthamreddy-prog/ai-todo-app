from fastapi import FastAPI,Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base,Session

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline

app=FastAPI() #used to initialize the FastAPI application

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 3. The "Session" is what we use to execute transactions (queries)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The "Base" is the blueprint we use to create our tables
Base = declarative_base()

class DBTask(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String, default="pending")

# 3. create_all is run THIRD (It must be BELOW the DBTask class!)
Base.metadata.create_all(bind=engine)

class Task(BaseModel):
    title: str
    status: str = "pending"
    
# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#defining function for endpoint(a GET request)

# ML Training Block
training_titles = [
    "Learn FastAPI", "Read documentation", "Finish hackathon project", 
    "Write essay", "Buy groceries", "Fix bugs in code", 
    "Build frontend prototype", "Prepare for mid-term examinations",
    "Clean the house", "Deploy application to cloud",
    "Read a book", "Read chapters for class", "Quick email reply",
    "Long database migration", "Study Python algorithms", "Take a nap"
]

# Match the new tasks with their realistic day estimates
training_days = [
    3.0, 1.0, 5.0, 
    7.0, 0.5, 2.0, 
    4.0, 10.0, 
    1.0, 3.5,
    1.5, 0.5, 0.1,  # Read a book, Read chapters, email
    5.0, 2.5, 0.1   # DB migration, Study Python, nap
]

ml_model = make_pipeline(TfidfVectorizer(), Ridge())
ml_model.fit(training_titles, training_days)
print("✅ Machine Learning Model Trained and Ready!")

# API ENDPOINTS (CRUD)
@app.get("/")
def read_root():
    return {"message":"Hello Web! The API is running."}

@app.get("/tasks")
def get_task(db: Session = Depends(get_db)):
    tasks=db.query(DBTask).all()
    result = [{"id": task.id, "title": task.title, "status": task.status} for task in tasks]
    return result

@app.post("/tasks")
def create_new_task(incoming_data: Task,db: Session= Depends(get_db)):
    # 1. Convert the Pydantic internet data into a SQLAlchemy database row
    new_db_task = DBTask(title=incoming_data.title, status=incoming_data.status)
    
    # 2. Add it to the session
    db.add(new_db_task)
    
    # 3. Commit the transaction (save it permanently)
    db.commit()
    
    # 4. Refresh to grab the newly auto-generated ID
    db.refresh(new_db_task)
    
    return {"message": f"Successfully added: {new_db_task.title}", "id": new_db_task.id}

# 4. The PUT Endpoint (Update)
@app.put("/tasks/{task_id}")
def update_task_status(task_id: int, db: Session = Depends(get_db)):
    # SQL Equivalent: SELECT * FROM tasks WHERE id = task_id LIMIT 1;
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    
    if task is None:
        return {"error": "Task not found"}
        
    # Update the status and save it permanently
    task.status = "completed"
    db.commit()
    
    return {"message": f"Task {task_id} marked as completed!"}

# 5. The DELETE Endpoint (Delete)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    # SQL Equivalent: SELECT * FROM tasks WHERE id = task_id LIMIT 1;
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    
    if task is None:
        return {"error": "Task not found"}
        
    # Delete the row and save the changes permanently
    db.delete(task)
    db.commit()
    
    return {"message": f"Deleted task: {task.title}"}

# AI Prediction ENDPOINT
@app.get("/predict")
def predict_task_time(title: str):
    predicted_days = ml_model.predict([title])[0]
    # Ensure it never predicts a negative number of days
    estimated_days = max(0.5, round(predicted_days, 1))
    
    return {
        "title": title, 
        "estimated_days": estimated_days
    }