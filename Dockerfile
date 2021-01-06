FROM python:2.7

RUN apt update
RUN apt install -yqq xinput x11-xserver-utils
RUN apt install -yqq python-gtk2 libappindicator1
CMD mkdir -p /opt/tmp/python-appindicator
CMD wget  --no-check-certificate 'http://my.opendesktop.org/s/gfCdMmfLaX627rj/download' -O /opt/tmp/python-appindicator/python-appindicator_0.4.92-4_amd64.deb
CMD dpkg -i /opt/tmp/python-appindicator/python-appindicator_0.4.92-4_amd64.deb
CMD apt-get install -f -y

# Add user so that container does not run as root 
RUN useradd -m docker 
RUN echo "docker:test" | chpasswd 
RUN usermod -s /bin/bash docker 
ENV HOME /home/docker

WORKDIR /usr/src/app

CMD ["bash"]
