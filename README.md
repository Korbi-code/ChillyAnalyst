# Chilly Analyst

## Install dependencies
This project is designed to be executed on Raspberry PI. 

Recommended os: 

### Docker and Docker-Compose
First step is to install docker and docker-compose. Both are needed! 

### Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
### Docker-Compose
```bash
sudo apt-get install python3-pip
sudo pip3 install docker-compose
```

## Execute this application

### Navigate into this repo 
```bash
cd <Path>/ChillyAnalyst
```
### Call docker-compose
Executing docker-compose command will do the follwing things: 
 1. build the image given in the Dockerfile
 2. Install all python related dependencies based on requirement.txt via pip
 3. Call the python application
 
 NOTE: First time executing this command will take several minutes  

```bash
sudo docker-compose up -d
```

### Rebuild
With updating this repo especially when requirements.txt has changed it can be necessary to rebuild the docker image: 
```bash
sudo docker-compose up --build 
```

### Shut down docker-compose
```bash
sudo docker-compose down
```