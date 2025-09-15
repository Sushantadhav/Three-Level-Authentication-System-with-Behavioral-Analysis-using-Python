# Step 1: Base image (Python ka version)
FROM python:3.11-slim

# Step 2: System dependencies install karo (numpy/pandas ke liye zaroori)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gcc g++ \
    libfreetype6-dev libpng-dev libatlas-base-dev gfortran && \
    rm -rf /var/lib/apt/lists/*

# Step 3: App ka folder set karo
WORKDIR /app

# Step 4: Requirements install karo
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Step 5: Apna code copy karo
COPY . .

# Step 6: Port set karo
ENV PORT=5000

# Step 7: Run command (gunicorn ke sath)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "3"]
