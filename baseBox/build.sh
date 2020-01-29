#!/usr/bin/env bash 
VERSION=${VERSION:-'6.3.5'}
echo "Building base image for version $VERSION"
rm -fv *.box 
vagrant destroy -f  || echo "Failed to remove previous image " && echo "Removed old image"
vagrant halt 
echo "Updating Vagrant File version"
sed  -e "s/SET_VERSION/$VERSION/" Vagrantfile.template > Vagrantfile
vagrant up 
vagrant package --output netsage-base.box
vagrant box add netsage-base/$VERSION netsage-base.box --force

if [ $? -eq 0 ]
then
    rm -fv *.box 
   echo "Removing box Image"
fi
