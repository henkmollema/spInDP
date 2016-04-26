# Configuration

1. Add your python script to `startspider`
2. Open `spiderboot.service` and change the line containing `ExecStart` to:
	```
	ExecStart=<Path to file>/startspider
	```
3. Add the service to systemd with the following line:
	```
	sudo systemctl enable /<Path to Service>/spiderboot.service
	```
4. Test if the service is working with:
	sudo systemctl start spiderboot.service
5. Reboot to check if the service starts on boot.

Reference:
https://gauntface.com/blog/2015/12/02/start-up-scripts-for-raspbian
