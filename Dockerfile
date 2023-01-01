FROM ubuntu


ENV USER ifueko

RUN apt-get update && apt-get install -y sudo
RUN adduser --disabled-password --gecos '' $USER
RUN adduser $USER sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN apt -y update
RUN apt -y install python3.10 python3-pip vim tmux
RUN pip install --upgrade pip
RUN pip install openai matplotlib plotly scipy scikit-learn tqdm


USER $USER
RUN sudo rm /bin/sh && sudo ln -s /bin/bash /bin/sh
RUN sudo ln -s /bin/python3 /bin/python


ENV DISPLAY :0
RUN sudo apt -y install x11-apps

WORKDIR /home/ifueko/course_scraper
