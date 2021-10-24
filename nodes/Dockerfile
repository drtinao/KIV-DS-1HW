#
# Use base image, install python and run script with implemented bully algo - controller.py
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest
RUN yum -q -y install python3
ADD main.py /home/main.py
ADD netTools.py /home/netTools.py
ADD nodeTools.py /home/nodeTools.py
ADD supportTools.py /home/supportTools.py
