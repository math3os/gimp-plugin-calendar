On ubuntu 20.04 those libs are not available from repo and are needed to allow gimp python plugin

Those ones comes from packages.debian.org

procedure:
Install some dependencies from repo with apt 
then, install those .deb package with `dpkg`

```
sudo apt install python-cairo python-gobject-2
sudo dpkg -i python-gtk2_2.24.0-5.1+b1_amd64.deb gimp-python_2.10.8-2_amd64.deb
```

