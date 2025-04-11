# Dockerfile to build and run the dashboard as a containerized service.
# Should expose the port Streamlit runs on and include all necessary libraries.

FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
