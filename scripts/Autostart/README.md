#CONFIGURATION
1. Open spiderboot.service
2. Change the line containing "ExecStart" so it points to the right .py file
3. Move spiderboot.service to /lib/systemd/system/spiderboot.service
4. Add the service to systemd with the following line:
	sudo systemctl enable /lib/systemd/system/spiderboot.service

The service is now automatically started on boot time.

5. Try to start the service manually by typing
	sudo systemctl start spiderboot.service
6. If you think something went wrong, then type:
	sudo systemctl status spiderboot.service