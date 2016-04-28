# RPi Setup

## RPi updaten
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo rpi-update
```

## Console signalen op `/dev/ttyAMA0` uitzetten
- Open terminal
- `raspi-config`
- Optie 9: Advanced Options
- Optie A8: Serial
- Kies `No`
- `Finish`
- Reboot? -> `Yes`

## Bluetooth op seriele poort uitzetten:
Open `boot/config.txt`:
`sudo nano /boot/config.txt`

Voeg deze regel onderaan toe:
```
dtoverlay=pi3-miniuart-bt
```

Open `/lib/systemd/system/hciuart.server` en vervang `ttyAMA0` met `ttyS0`

https://www.raspberrypi.org/forums/viewtopic.php?t=138223&p=918859

Stop Bluetooth modem:
```
sudo systemctl disable hciuart
```

Reboot

## Baudraute aanpassen
```
sudo stty -F /dev/ttyAMA0 1000000
```
```
sudo stty -F /dev/serial0 1000000
```

GPIO pinnen 14 en 15 op mode `ALT0` zetten:
```
gpio -g mode 14 alt0
gpio -g mode 15 alt0
```

`/dev/ttyAMA0` stoppen
```
sudo systemctl stop getty.target
```

Alle poorten bekijken:
```
gpio readall
```
