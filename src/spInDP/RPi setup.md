# RPi Setup

Baudraute aanpassen
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
