# RPi Home Server instructions

## Set-up the pi with basics

### Fresh SD card
Put an empty 'ssh' file into boot directory to enable headless mode with ssh activated. 

### Update & Upgrade
```
sudo apt update
sudo apt upgrade
sudo apt clean
```

Install emacs & python3
```
sudo apt install emacs
sudo apt install python3-pip
```

### Connect to Wifi
(on a clean SD card, put such a *wpa_supplicant.conf* file into boot directory to add it to the pi automatically)

```
sudo emacs /etc/wpa_supplicant/wpa_supplicant.conf
```

Insert (change country code if required):
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={
 ssid="SSID"
 psk="PASSWORD"
 priority=1
 id_str="home"
}

network={
 ssid="repair"
 psk="repair_pwd"
 priority=2
 id_str="repair"
}
```
The second wifi is added in case the first one does not work, to still be able to access the pi. If the pi has an Ethernet port, that can also be used for debugging and making sure that the pi has (wifi) connectivity.

## Install home server code
Perhaps reboot now to make sure the pi is connected and accessible again over ssh:
```
sudo reboot
```
Reconnect (replace with the assigned IP address):
```
ssh pi@192.168.0.188
```
Once connected it you can change the pi's default password using the command:
```
passwd
```
This is recommended. 


Go into user's home directory and clone from github:
```
cd
git clone https://github.com/paulodicanio86/home_server.git
```
Now a folder *home_server* should appear in the user's home directory 

### Set up a virtual environment
Go into that new directory and execute:
```
sudo apt install python3-venv
python3 -m venv venv_app
```
Activate the newly created virtual environment and install packages:
```
source venv_app/bin/activate
pip3 install -r requirements.txt
```
If not done already, these packages should have been included. Manually you can also do:
```
pip3 install RPi.GPIO flask uwsgi
```

To check what's installed in the environment do:
```
pip3 freeze
```
Deactivate venv for now:
```
deactivate
```

## Prepare the webserver
### Install nginx
```
sudo apt install nginx
```
Run server:
```
sudo service nginx start
```

### Install & prepare uWSGI
```
sudo pip install uwsgi
```

There should already be a file (from git clone) in the home server directory called *wsgi.py* with following content (if not create one):
```
from app import app

if __name__ == "__main__":
    app.run()
```

There should already be a file (from git clone) in the home server directory called *home_server.ini* with following content (if not create one):
```
[uwsgi]
module = wsgi:app

master = true
processes = 4

uid = www-data
gid = www-data

socket = /tmp/home_server.sock
chmod-socket = 664
vacuum = true

die-on-term = true
touch-reload = /home/pi/home_server/rpiserver/views.py
```

### Make some extra changes required
Let the webserver access the GPIO pins:
```
sudo adduser www-data gpio
```

Let the webserver edit (read & write) the *schedule.json* file (go to the home server directory):
```
chmod 666 schedule.json
```

### Configure nginx to use uWSGI
Delete the default nginx site:
```
sudo rm /etc/nginx/sites-enabled/default
```

Make a new site:
```
sudo emacs /etc/nginx/sites-available/home_server
```
Add following content:
```
server {
    listen 80;
    server_name localhost;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/home_server.sock;
    }
}
```
Make a shortcut (or link) of this file to the enabled sites folder:
```
sudo ln -s /etc/nginx/sites-available/home_server /etc/nginx/sites-enabled
```

Restart the nginx server:
```
sudo systemctl restart nginx
```

### Run uWSGI when pi boots:
Create a new service in the system's start up folder:
```
sudo emacs /etc/systemd/system/home_server.service
```
Add following content (to start the venv and execute uwsgi):
```
[Unit]
Description=uWSGI instance to serve home_server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/pi/home_server
Environment="PATH=/home/pi/home_server/venv_app/bin"
ExecStart=/home/pi/home_server/venv_app/bin/uwsgi --ini /home/pi/home_server/home_server.ini

[Install]
WantedBy=multi-user.target
```

To start this process right now, you can do:
```
sudo systemctl daemon-reload
sudo systemctl start home_server.service
```
Test if it runs:
```
sudo systemctl status home_server.service
```
This should be an active process now. 

Enable it for when the pi reboots:
```
sudo systemctl enable  home_server.service
```

## Test & Finish
Reboot:
```
sudo reboot
```
Check if nginx is running:
```
sudo systemctl status nginx
```
Check if uWSGI is running:
```
sudo systemctl status home_server.service
```

If both are running, you should now see your app running when you access the pi in a browser:
```
http://192.168.0.188
```
(replace with the assigned IP address)


## Create cron job to check for jobs every minute
View all jobs:
```
crontab -l
```
Make a new job:
```
crontab -e
```

Add:
```
* * * * * /usr/bin/python3 /home/pi/home_server/scheduler.py
```
This executes this python script every minute.

## Set a fixed IP address
This is so that you can always access the server under the same address. Be aware of this! Make sure it is an address outside the network's DHCP range, otherwise clashes can occur.
Edit the following file:
```
sudo emacs /etc/dhcpcd.conf
```
Add to the bottom:
```
interface eth0
	static ip_address=192.168.0.50/24
        static routers=192.168.0.1
        static domain_name_servers=127.0.0.1
```
In this case 192.168.0.50 is the new fixed IP address, 192.168.0.1 is the router in the LAN. To fix the IP address of the wifi replace *eth0* with *wlan0*. 

Reboot:
```
sudo reboot
```
Access via new IP address (if it worked!):
```
ssh pi@192.168.0.50
```
See the new IP address:
```
ifconfig
```

















