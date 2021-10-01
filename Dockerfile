FROM python:3.8
RUN pip install --upgrade pip

#RUN apt-get update   		            && \
# 	apt-get install vim -y

#WORKDIR /src
#RUN pip install -U pymt5adapter
#RUN apt-get install ntpdate -y

WORKDIR /
#ADD ./requirements.txt /requirements.txt
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# or remove rarc dependency by creating a slack-utils repo
# RUN --mount=type=ssh,id=github_ssh_key pip install --force-reinstall --upgrade git+https://github.com/paulbroek/rarc.git

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# add new packages here, later add them to requirements.txt
# RUN pip install --no-cache-dir pytest

# Extract weblogic
RUN rm -rf /tmp/*