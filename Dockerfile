FROM ubuntu:20.04
ENV TZ=America/New_York
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /install
ADD ubuntu-20.04-missing-libs/* ./
RUN apt-get update && apt-get install -y \
    aptitude \
    cargo-1.80 \
    locales \
    fonts-open-sans \
    fonts-roboto \
    fonts-lato \
    gimp \
    python-cairo python-gobject-2 \
    python-is-python2 python-numpy \
    python-pkg-resources \
    python-yaml \
    && dpkg -i *.deb && rm *
ARG UID
RUN useradd -u "${UID}" -m gimp
RUN echo '(plug-in-path "${gimp_dir}/plug-ins:${gimp_plug_in_dir}/plug-ins:/gimp/src")' >> /etc/gimp/2.0/gimprc &&  \
    echo '(font-path "${gimp_dir}/fonts:${gimp_data_dir}/fonts:/gimp/font")' >> /etc/gimp/2.0/gimprc

USER gimp
RUN cargo-1.80 install moontool --version 1.2.0 --locked -F rich-output
ENV PATH="$PATH:/home/gimp/.cargo/bin"

CMD ["/usr/bin/gimp"]
