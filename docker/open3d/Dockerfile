FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
  git \
  python3 \
  python3-pip \
  xorg-dev \
  libglu1-mesa-dev \
  python3-dev \
  libosmesa6-dev \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/intel-isl/Open3D /root/open3d
RUN pip3 install open3d
RUN mkdir -p /root/workspace/
COPY create_config.py /root/workspace/create_config.py
COPY integrate.sh /root/workspace/integrate.sh
RUN chmod +x /root/workspace/integrate.sh

ENTRYPOINT ["/root/workspace/integrate.sh", "/root/dataset/"]

