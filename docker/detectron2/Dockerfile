FROM nvidia/cuda:11.1.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build freeglut3-dev
RUN ln -sv /usr/bin/python3 /usr/bin/python
RUN wget https://bootstrap.pypa.io/get-pip.py && \
	python3 get-pip.py && \
	rm get-pip.py
ENV FORCE_CUDA="1"
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN pip install torch==1.9 torchvision==0.10 -f https://download.pytorch.org/whl/cu111/torch_stable.html
RUN pip install git+https://github.com/facebookresearch/detectron2.git@v0.5

RUN mkdir -p /root/workspace/

COPY --chown=user straylib /tmp/straylib
RUN pip3 install /tmp/straylib
RUN rm -rf /tmp/straylib

COPY --chown=user model /tmp/straymodel
RUN pip3 install /tmp/straymodel
RUN rm -rf /tmp/straymodel

ENV FVCORE_CACHE="/tmp"

COPY ./entrypoint.sh /root/workspace/entrypoint.sh
RUN chmod +x /root/workspace/entrypoint.sh

ENTRYPOINT ["/root/workspace/entrypoint.sh"]
CMD []