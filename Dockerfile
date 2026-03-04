FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# No need to run 'playwright install' manually, the image above has it!
CMD ["streamlit", "run", "app.py", "--server.port", "8080"]