# Chilly Analyst

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
git checkout origin/feature/tasmota-plugin-v02
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

- Congrats, you finished the installation, now you can eat your second banana while the system reboots! 
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

