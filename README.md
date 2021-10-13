# Chilly Analyst
[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/Korbi-code/ChillyAnalyst/?ref=repository-badge)

# Description
You are annoyed by your washing machine because the displayed time at the beginning of the programm was not correct ?  
You want to get a notifiaction to your smartphone when the programm is finished ? 
..
..
Then we have a solution!  

## How does it work ? 
By setting up a small script which is reading the current power from a compatible wall plug, observe the power level and sends a notifcation via your own Telegram bot to your device which is running the Telegram messenger app. 

## What do I need ? 
- Device which can run a python 3.8 Script with internet connection (Raspberry Pi recommended) 
- Telegram Application
- Wall plug with power measurement running Tasmota Firmware

# Setup

1. Install Raspberry Pi OS
- Download imager, open application and install Os to your SD-card
- https://www.raspberrypi.org/software/

- Tested with Full Pi OS Desktop installation approx. 2.5GB
    - Light version can work, but it is not tested

 
2. Connect hardware
- Fire up your Raspberry Pi (e.g connect 5V)


3. Configure your Raspberry Pi
 - Connect with Wifi or Lan
 - Open Raspberry Pi config    
```bash
sudo raspi-config
```
 - Interfacing Options -> Enable SSH
 - Set Hostname to "chillyanalyst"

3. Reboot your Raspberry Pi
```bash
sudo reboot
```   

4. Install git, python3 and docker-compose (most likely it will already be installed)
```bash
sudo apt install git 
sudo apt-get install python3-pip
``` 


5. Clone ChillyAnalyst repository to your Raspberry Pi
```bash
git clone https://github.com/Korbi-code/ChillyAnalyst.git
cd ChillyAnalyst
git checkout origin/master
```   

6. Install python dependencies
```bash
cd ChillyAnalyst
sudo pip3 install -r requirements.txt
```     

7. Configure your Telegram-Bot 
    - Open telegram application on a smartphone or web application
    - Search "BotFather"
    - Create a Bot by following the instructions until your get the access token
    
    
8. Add access token to config file
```bash
sudo nano ChillyAnalyst/config/config.cfg
```   
- paste your unique telegram access token into the config file (Hint: login into Telegram via browser to copy)
- choose your personal password 
- Confirm bash with:
    - Strg + O 
    - Strg + X

9. Enable Autostart services
- To automatically start the python script copy the provided service into your system lib and enable the service
```bash
cd ChillyAnalyst
sudo cp chillyanalyst.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable chillyanalyst.service
```  

10. Final reboot

- Congrats, you finished the installation!
```bash
sudo reboot
``` 

11. Updates

- For updating the program  
```bash
cd ChillyAnalyst
git fetch
git pull
sudo systemctl restart chillyanalyst.service
``` 

# Design Doc

Parameter Description

| NAME          | Description   
| ------------- |:-------------:|
| PARAM_POWER_LOWER_LEVEL         | Power level to detect start after filter
| PARAM_POWER_DEBOUNCE_LEVEL      | When power is below this level debouncing is active    
| PARAM_EMETER_PLUG_RESOLUTION    | Factor to convert raw power to power in [W]  
| PARAM_IDLE_TICK_RATE            | Read power rate during idle state      
| PARAM_MEASURE_TICK_RATE         | Read power rate during measure phase e.g after start till end     
| PARAM_DEBOUNCE_TICK_LIMIT       | Amount of ticks power level can be at or below PARAM_POWER_DEBOUNCE_LEVEL, if so "end" is detected       
| FILTER_QUEUE                    | Size of fifo queue to calculate the mean value 


Input filtering

![Alt text](doc/Input.png?raw=true "Input Filter")


State Timing

![Alt text](doc/StateTiming.png?raw=true "State Timing")
