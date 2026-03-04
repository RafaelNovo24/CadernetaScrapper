# Use the official Microsoft Playwright image which includes Python and Browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the Chromium browser (Playwright's image has the libs, but we need the binaries)
RUN playwright install chromium

# Copy the rest of your application code
COPY . .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8501

# Command to run the app
# --server.address=0.0.0.0 is required for cloud hosting
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]