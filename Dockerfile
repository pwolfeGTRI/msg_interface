FROM pwolfe854/gst_ds_env:x86_64_nogpu

# google protobufs installation for use with C++ and python 3.5 - 3.7 preinstalled in base image now

# install skaimsginterface as a python package
COPY package /root/package
RUN cd /root/package && ./install_skaimsginterface.sh
# note this copies the same folder being mapped in this case.
# feel free to put it wherever in your docker

# working on the cpp classes now...
RUN apt-get install -y cmake