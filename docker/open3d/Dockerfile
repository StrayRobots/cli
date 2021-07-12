FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  git \
  python3.8 \
  libgit2-dev \
  xorg-dev \
  libglu1-mesa-dev \
  python3-dev \
  libosmesa6-dev \
  python3-opencv \
  wget

RUN rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.8 get-pip.py
RUN rm get-pip.py

RUN pip3 install dvc[s3] open3d

RUN git clone https://github.com/intel-isl/Open3D /tmp/open3d && cd /tmp/open3d/ && git checkout v0.13.0
RUN mv /tmp/open3d/examples/python/ /root/open3d/
RUN rm -rf /tmp/open3d
RUN rm -rf /root/.cache

RUN mkdir -p /root/workspace/
COPY gitconfig /root/.gitconfig
COPY create_config.py /root/workspace/create_config.py
COPY integrate.sh /root/workspace/integrate.sh
RUN chmod +x /root/workspace/integrate.sh

RUN mkdir /root/.ssh
COPY id_integration.pub /root/.ssh/id_integration.pub
RUN chmod 664 /root/.ssh/id_integration.pub
COPY ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config

ENTRYPOINT ["/root/workspace/integrate.sh"]

