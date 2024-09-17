FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install mysql-connector-python==8.4.0
RUN pip install Flask==3.0.3
RUN pip install Flask-SocketIO==5.3.6
RUN pip install Flask['async']
RUN pip install Jinja2==3.1.4
RUN pip install passlib==1.7.4
RUN pip install pillow==10.3.0
RUN pip install python-engineio==4.9.1
RUN pip install python-socketio==5.11.3
RUN pip install requests==2.32.3

EXPOSE 5000

CMD ["python", "app.py"]

