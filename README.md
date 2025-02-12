# Plugin calendar for Gimp
once src/ folder is added to gimp plugin path into settings/folder/plugin
a menu calendar should appears into gimp's menubar

On linux, you can launch gimp from docker-compose

## docker-compose on linux
copy file .env.example to .env
adjust UID and GID value

install docker
install docker-compose

 then run 
 ```
 docker-compose up
 ```

it should launch gimp auto-magically.
