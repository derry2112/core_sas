# Menggunakan base image Python
FROM python:3.9

# Set working directory
WORKDIR /app

# Menyalin file requirements.txt dan menginstal dependensi
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua file aplikasi ke dalam container
COPY . .

# Menentukan port yang akan digunakan
EXPOSE 8000

# Menjalankan aplikasi menggunakan Uvicorn
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


