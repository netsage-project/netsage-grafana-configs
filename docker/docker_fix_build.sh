#!/usr/bin/env bash

#export N_PREFIX="$HOME/n"; [[ :$PATH: == *":$N_PREFIX/bin:"* ]] || PATH+=":$N_PREFIX/bin"  # Added by n-install (see http://git.io/n-install-repo).
for dir in $(find ../plugins -iname "Makefile")
do
  sed -i -e 's/echo systemctl/systemctl/g' $dir  # Undo previous change if it exists
  sed -i -e 's/systemctl/echo systemctl/g' -e 's/sudo //g' $dir  # Disable systemd restart
  sed -i -e 's/rpmbuild/rpmbuild --nodeps/g' $dir
done

 