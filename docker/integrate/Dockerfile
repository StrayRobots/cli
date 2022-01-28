FROM nvidia/cuda:10.2-base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  git \
  xorg-dev \
  libglu1-mesa-dev \
  libpython2.7-dev \
  python-opencv \
  python3.8-dev \
  python3.8-distutils \
  cmake \
  python-pip \
  libglew-dev \
  libopencv-dev \
  libboost-dev \
  libeigen3-dev \
  libssl-dev \
  libomp-dev \
  libboost-serialization-dev \
  wget \
  unzip

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user

ENV PATH="/home/user/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.8 get-pip.py
RUN rm get-pip.py

COPY --chown=user:sudo straylib /tmp/straylib
WORKDIR /tmp/straylib
RUN python3.8 setup.py bdist_egg --exclude-source-files
RUN wheel convert $(find dist/straylib-*.egg)
RUN pip3.8 install "$(basename $(find straylib-*.whl))"
RUN rm -rf /tmp/straylib

RUN pip3 install --user open3d==0.14.1 opencv-python scipy numpy PyYAML click trimesh requests && rm -rf /user/.cache

RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

RUN wget https://github.com/alicevision/meshroom/releases/download/v2021.1.0/Meshroom-2021.1.0-linux-cuda10.tar.gz
RUN chown user:sudo /home/user/workspace/Meshroom-2021.1.0-linux-cuda10.tar.gz
RUN tar -xf /home/user/workspace/Meshroom-2021.1.0-linux-cuda10.tar.gz

COPY docker/integrate/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/integrate/create_sfm.py /home/user/workspace/create_sfm.py
COPY docker/integrate/combine_trajectories.py /home/user/workspace/combine_trajectories.py
COPY docker/validate_license.py /home/user/workspace/validate_license.py
COPY docker/integrate/pipeline.mg /home/user/workspace/pipeline.mg
COPY docker/orbslam/integrate.py /home/user/workspace/integrate.py
COPY docker/orbslam/integrate_pointcloud.py /home/user/workspace/integrate_pointcloud.py


ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []

