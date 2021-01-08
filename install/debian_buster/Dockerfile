FROM debian:buster

RUN apt update
RUN apt install -yqq python3
RUN apt install -yqq xinput x11-xserver-utils
RUN apt install -yqq python-gobject python3-gi gir1.2-gtk-3.0
RUN apt install -yqq gir1.2-appindicator3

# Add user so that container does not run as root 
RUN useradd -m docker 
RUN echo "docker:test" | chpasswd 
RUN usermod -s /bin/bash docker 
ENV HOME /home/docker

WORKDIR /usr/src/app

CMD ["bash"]
