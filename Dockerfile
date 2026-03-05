FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install only Chromium to save space and memory
RUN playwright install chromium --with-deps

COPY . .

# Render uses the PORT environment variable automatically
EXPOSE 8000

CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]

# docker run -p 8000:8000 my-app   