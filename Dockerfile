FROM acceleratorbase/openvino-base

ARG HOSTNAME
ENV NODE_NAME=$HOSTNAME

ADD . /app/
WORKDIR /app
RUN python3 setup.py install

CMD [ "ncs2_device_plugin" ]
