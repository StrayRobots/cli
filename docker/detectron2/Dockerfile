
FROM nvidia/cuda:11.1.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build freeglut3-dev
RUN ln -sv /usr/bin/python3 /usr/bin/python

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
WORKDIR /home/appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py --user && \
	rm get-pip.py

# install dependencies
# See https://pytorch.org/ for other options if you use a different version of CUDA
RUN pip install --user tensorboard cmake   # cmake from apt-get is too old
RUN pip install --user torch==1.9 torchvision==0.10 -f https://download.pytorch.org/whl/cu111/torch_stable.html

RUN pip install --user 'git+git://github.com/facebookresearch/fvcore.git@2d073f1b713f6ff3bb310af9a4313a5e8e03f49c'
# install detectron2
RUN git clone --depth 1 --branch v0.4 https://github.com/facebookresearch/detectron2 detectron2_repo
# set FORCE_CUDA because during `docker build` cuda is not accessible
ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN pip install --user -e detectron2_repo

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"

COPY . /home/appuser/CLI
RUN sudo rm -rf /home/appuser/CLI/straylib/straylib.egg-info
RUN sudo rm -rf /home/appuser/CLI/model/straymodel.egg-info
RUN sudo rm -rf /home/appuser/CLI/label/straylabel.egg-info

RUN pip install CLI/straylib
RUN pip install -r CLI/straylib/requirements.txt

RUN pip install CLI/model
RUN pip install -r CLI/model/requirements.txt

RUN pip install CLI/label
RUN pip install -r CLI/label/requirements.txt

RUN mkdir models
