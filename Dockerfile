FROM python:3

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.lock

# -u flag to avoid buffering of stdout so that logs are printed in real time
CMD ["python", "-u","newshound.py"] 
