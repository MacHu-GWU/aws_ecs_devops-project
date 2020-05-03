FROM python:3.6.2-slim
COPY ./ /var/app
RUN pip install /var/app --no-cache-dir
ENV FLASK_APP="/var/app/docker-repos/webapp/app.py"
ENV FLASK_RUN_HOST="0.0.0.0"
ENV FLASK_RUN_PORT="80"
ENTRYPOINT [ "flask", "run"]
