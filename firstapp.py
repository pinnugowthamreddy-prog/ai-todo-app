import streamlit as st
import requests
import pandas as pd
import random

st.title("My To-Do App")

st.header("Day 3:The Full_Stack Connection")

API_URL = "https://ai-todo-app-fefe.onrender.com" # Forced update

new_task=st.text_input("Enter a new task:")

# --- NEW AI PREDICTION UI ---
# If the user has typed anything into the box, ask FastAPI for a prediction!
if new_task:
    # We alter your existing API_URL to point to the new /predict endpoint
    base_url = API_URL.replace("/tasks", "")
    predict_url = f"{base_url}/predict?title={new_task}"
    
    try:
        ai_response = requests.get(predict_url)
        if ai_response.status_code == 200:
            estimate = ai_response.json()["estimated_days"]
            st.success(f"🤖 **AI Estimate:** Based on historical patterns, this task will take about **{estimate} days**.")
    except:
        pass # If the AI isn't ready, just fail silently so the app doesn't crash
# -----------------------------

if st.button("Add Task"):
    if new_task:
        task_data={
            "title":new_task,
            "status":"pending"
        }
        response=requests.post(API_URL,json=task_data)
        if response.status_code==200:
            st.success(f"Successfully added to list: '{new_task}'")
        else:
            st.error("Failed to add task.")
    else:
        st.error("Please enter a task first!")
        
st.divider()

# -----------------------------------------
# PART 2: READING DATA FROM FASTAPI (GET) & ANALYTICS
# -----------------------------------------
st.subheader("Your Tasks")

response = requests.get(API_URL)

# IMMEDIATELY check the status code before doing anything else!
if response.status_code == 200:
    tasks = response.json()
    
    if len(tasks) > 0:
        # Only create the DataFrame safely inside here
        df = pd.DataFrame(tasks)
        
        # ... (Your custom analytics go here) ...
        
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No tasks found. Add one above to see your analytics!")
else:
    st.error(f"FastAPI Error Code: {response.status_code}")
    st.write("Raw response from server:")
    st.write(response.text)
        
# --- NEW ANALYTICS SECTION ---
# Calculate our key metrics
total_tasks = len(df)
completed_tasks = len(df[df["status"] == "completed"])
pending_tasks = len(df[df["status"] == "pending"])
completion_rate = round((completed_tasks / total_tasks) * 100)
        
# Display metrics in 4 columns across the top
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tasks", total_tasks)
m2.metric("Pending", pending_tasks)
m3.metric("Completed", completed_tasks)
m4.metric("Completion Rate", f"{completion_rate}%")
        
# Add a visual progress bar based on the completion rate
st.progress(completion_rate / 100)
st.divider()
        
# --- NEW CHART SECTION ---
st.write("### Workload Distribution")
        
# Count how many tasks are in each status using Pandas
status_counts = df["status"].value_counts()
        
# Display an interactive bar chart
st.bar_chart(status_counts, color="#ff4b4b")
    
st.divider()

st.subheader("Manage Tasks")

col1, col2, col3=st.columns([2,1,1],vertical_alignment="bottom")

with col1:
    target_id=st.number_input("Enter Task ID to manage:",min_value=1,step=1)

with col2:
    if st.button("Mark Completed", use_container_width=True):
        response=requests.put(f"{API_URL}/{target_id}")
        if "error" not in response.json():
            st.rerun()
        else:
            st.error("Task not found!")
            
with col3:
    if st.button("Delete Task", use_container_width=True):
        response=requests.delete(f"{API_URL}/{target_id}")
        if "error" not in response.json():
            st.rerun()
        else:
            st.error("Task not found!")