FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn for production (eventlet worker for WebSocket support)
# Note: Flask-SocketIO automatically integrates with app when eventlet is detected
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--worker-class", "eventlet", "--timeout", "120", "src.app:app"]
