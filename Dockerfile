FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=yes
ENV PYTHONDONTWRITEBYTECODE=yes

WORKDIR /tmp

COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY ./kube-viktor /opt/kube-viktor

WORKDIR /opt/kube-viktor

RUN chmod +x /opt/kube-viktor/main.py

ENTRYPOINT ["/usr/local/bin/python", "/opt/kube-viktor/main.py"]
CMD [""]
