#!/bin/bash
source ssh-credentials

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping running services...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl stop python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service stopped${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl disable python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service disabled${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl stop python-blinds-webserver.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service stopped${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl disable python-blinds-webserver.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service disabled${NC}"

echo -e "${BLUE}Replacing <username> with $USER in python-blinds.service and python-blinds-webserver.service...${NC}"
sed -i "s/<username>/$USER/g" python-blinds.service
sed -i "s/<username>/$USER/g" python-blinds-webserver.service

echo -e "${BLUE}Copying python files...${NC}"
scp -r blinds/*.py $USER@$DESTINATION:/home/$USER/workspace/python-blinds/blinds

echo -e "${BLUE}Copying python webserver and ui files...${NC}"
scp -r webserver/dist/index.js $USER@$DESTINATION:/home/$USER/workspace/python-blinds/webserver/index.js
scp -r ui/dist/* $USER@$DESTINATION:/home/$USER/workspace/python-blinds/webserver/ui

echo -e "${BLUE}Copying python blinds service and start script...${NC}"
scp -r python-blinds.service $USER@$DESTINATION:/home/$USER/workspace/python-blinds
scp -r python-blinds-webserver.service $USER@$DESTINATION:/home/$USER/workspace/python-blinds

echo -e "${BLUE}Moving python-blinds.service to /lib/systemd/system and set permissions...${NC}"
ssh -t $USER@$DESTINATION "sudo mv /home/$USER/workspace/python-blinds/python-blinds.service /lib/systemd/system" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service moved to /lib/systemd/system${NC}"
ssh -t $USER@$DESTINATION "sudo chmod 644 /lib/systemd/system/python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service permissions set${NC}"

echo -e "${BLUE}Moving python-blinds-webserver.service to /lib/systemd/system and set permissions...${NC}"
ssh -t $USER@$DESTINATION "sudo mv /home/$USER/workspace/python-blinds/python-blinds-webserver.service /lib/systemd/system" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service moved to /lib/systemd/system${NC}"
ssh -t $USER@$DESTINATION "sudo chmod 644 /lib/systemd/system/python-blinds-webserver.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service permissions set${NC}"

echo -e "${BLUE}Restarting systemd...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl daemon-reload" > /dev/null 2>&1 && echo -e "${GREEN}systemd daemon reloaded${NC}"

echo -e "${BLUE}Enabling python-blinds service and restart it...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl enable python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service enabled${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl restart python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds.service restarted${NC}"

echo -e "${BLUE}Enabling python-blinds-webserver service and restart it...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl enable python-blinds-webserver.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service enabled${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl restart python-blinds-webserver.service" > /dev/null 2>&1 && echo -e "${GREEN}python-blinds-webserver.service restarted${NC}"