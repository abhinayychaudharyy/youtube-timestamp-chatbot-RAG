@echo off
echo Starting YouTube RAG Services...
echo ===================================

echo Starting FastAPI Backend on port 8000...
start cmd /k "venv\Scripts\python.exe run.py"

echo Starting Streamlit Frontend...
set STREAMLIT_EMAIL=
start cmd /k "set STREAMLIT_EMAIL= && venv\Scripts\python.exe -m streamlit run streamlit_app.py"

echo Both services have been started in separate terminal windows.
echo Please leave those windows open while using the app.
