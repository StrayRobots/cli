FROM stereolabs/kalibr

RUN mkdir /root/workspace
COPY ./entrypoint.sh /root/workspace/entrypoint.sh
COPY convert_format.py /root/workspace/convert_format.py
COPY extract_calibration.py /root/workspace/extract_calibration.py
RUN python -m pip install pillow pyyaml

ENTRYPOINT ["/root/workspace/entrypoint.sh"]

