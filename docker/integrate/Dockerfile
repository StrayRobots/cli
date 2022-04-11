FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
  build-essential \
  git \
  xorg-dev \
  libglu1-mesa-dev \
  libpython2.7-dev \
  python3.8-dev \
  python3.8-distutils \
  cmake \
  libglew-dev \
  libopencv-dev \
  libboost-dev \
  libeigen3-dev \
  libssl-dev \
  libomp-dev \
  libboost-serialization-dev \
  qtbase5-dev \
  libqt5opengl5-dev \
  libcgal-dev \
  libsuitesparse-dev \
  libatlas-base-dev \
  libgflags-dev \
  libfreeimage-dev \
  libgoogle-glog-dev \
  libboost-graph-dev \
  libboost-test-dev \
  libboost-system-dev \
  libboost-filesystem-dev \
  libboost-program-options-dev \
  wget \
  unzip

RUN rm -rf /var/lib/apt/lists/*

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} user -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER user
WORKDIR /home/user

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/home/user/miniconda/bin:$PATH

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O ~/miniconda.sh \
  && chmod +x ~/miniconda.sh \
  && ~/miniconda.sh -b -p ~/miniconda \
  && rm ~/miniconda.sh

RUN python -m pip install --upgrade pip
RUN pip3 install open3d==0.14.1 opencv-python scipy numpy PyYAML click trimesh requests
RUN conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch

RUN git clone --recursive https://github.com/cvg/Hierarchical-Localization /home/user/hloc
RUN pip3 install -e /home/user/hloc

COPY --chown=user:sudo stray /tmp/stray
WORKDIR /tmp/stray
RUN pip3 install .
RUN rm -rf /tmp/stray

RUN conda clean -ya
# Include netvlad model for retrieval based matching.
RUN mkdir /home/user/hloc/third_party/netvlad && cd /home/user/hloc/third_party/netvlad && wget https://cvg-data.inf.ethz.ch/hloc/netvlad/Pitts30K_struct.mat -O VGG16-NetVLAD-Pitts30K.mat

RUN mkdir /home/user/workspace
WORKDIR /home/user/workspace

COPY docker/integrate/entrypoint.sh /home/user/workspace/entrypoint.sh
COPY docker/integrate/run_sfm.py /home/user/workspace/run_sfm.py
COPY docker/integrate/combine_trajectories.py /home/user/workspace/combine_trajectories.py
COPY docker/integrate/utils.py /home/user/workspace/utils.py
COPY docker/integrate/pipeline.mg /home/user/workspace/pipeline.mg
COPY docker/integrate/integrate.py /home/user/workspace/integrate.py
COPY docker/integrate/integrate_pointcloud.py /home/user/workspace/integrate_pointcloud.py

ENTRYPOINT ["/home/user/workspace/entrypoint.sh"]
CMD []

