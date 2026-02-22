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


### issue with wayland
$ docker compose up
```bash
[+] Running 1/1
 ✔ Container gimp-plugin-calendar2-gimp2-1  Created                                                                                                                   0.1s 
Attaching to gimp2-1
gimp2-1  | Authorization required, but no authorization protocol specified
gimp2-1  | Cannot open display: 
gimp2-1 exited with code 1
```

run this command:
```
xhost +local:docker
```