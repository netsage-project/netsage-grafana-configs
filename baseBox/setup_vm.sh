#!/usr/bin/env bash
## This script is invoked from the Vagrant file and can also be invoked on any RHEL server to perform a similar setup.
VERSION=${VERSION:-"6.3.5"}

yum install -y epel-release
yum clean all
yum install -y gcc\
    kernel-devel\
    kernel-headers\
    dkms\
    make\
    bzip2\
    perl\
    perl-devel\
    net-tools\
    nc \
    git\
    npm\
    rpm-build\
    gcc-c++\
    https://dl.grafana.com/oss/release/grafana-$VERSION-1.x86_64.rpm

