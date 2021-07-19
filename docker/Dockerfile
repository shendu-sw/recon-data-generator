FROM quay.io/fenicsproject/stable:current
LABEL maintainer="278954153@qq.com"

WORKDIR /tmp
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN pip install . && rm -rf *

USER fenics
RUN mkdir /home/fenics/layout
WORKDIR /home/fenics/layout
RUN layout_generator generate --worker 1 && rm -rf *
USER root
ENTRYPOINT [""]
