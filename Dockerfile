FROM python:3.9

RUN python -m pip install --upgrade pip

RUN apt-get update   		            && \
	apt-get install git -y				&& \
	apt-get install openssh-client

WORKDIR /

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY . /tmp

# install package
RUN pip install /tmp
