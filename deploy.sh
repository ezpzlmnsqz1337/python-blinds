#!/bin/bash
source ssh-credentials

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

MODE="full"

if [[ "${1:-}" == "--ui-only" ]]; then
	MODE="ui-only"
elif [[ $# -gt 0 ]]; then
	echo "Usage: bash deploy.sh [--ui-only]"
	exit 1
fi

REMOTE_ROOT="/home/$USER/workspace/python-blinds"
REMOTE_BLINDS="$REMOTE_ROOT/blinds"
REMOTE_UI_DIST="$REMOTE_ROOT/ui/dist"

if [[ "$MODE" == "ui-only" ]]; then
	echo -e "${BLUE}🎨 Running UI-only deploy...${NC}"
else
	echo -e "${BLUE}🛑 Stopping running services...${NC}"
	ssh -t $USER@$DESTINATION "sudo systemctl stop python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}✅ python-blinds.service stopped${NC}"

	echo -e "${BLUE}📁 Copying python files...${NC}"
	scp -r blinds/*.py $USER@$DESTINATION:$REMOTE_BLINDS

	echo -e "${BLUE}📄 Copying Python project files...${NC}"
	scp -r blinds/pyproject.toml $USER@$DESTINATION:$REMOTE_BLINDS
	scp -r blinds/README.md $USER@$DESTINATION:$REMOTE_BLINDS
	scp -r blinds/uv.lock $USER@$DESTINATION:$REMOTE_BLINDS
fi

echo -e "${BLUE}📦 Copying built UI files...${NC}"
ssh -t $USER@$DESTINATION "mkdir -p $REMOTE_UI_DIST" > /dev/null 2>&1
scp -r ui/dist/* $USER@$DESTINATION:$REMOTE_UI_DIST

if [[ "$MODE" == "ui-only" ]]; then
	echo -e "${GREEN}✅ UI deploy complete${NC}"
	exit 0
fi

echo -e "${BLUE}📋 Copying python blinds service and start script...${NC}"
scp -r python-blinds.service $USER@$DESTINATION:$REMOTE_ROOT

echo -e "${BLUE}➡️  Moving python-blinds.service to /lib/systemd/system and set permissions...${NC}"
ssh -t $USER@$DESTINATION "sudo mv $REMOTE_ROOT/python-blinds.service /lib/systemd/system" > /dev/null 2>&1 && echo -e "${GREEN}✅ python-blinds.service moved to /lib/systemd/system${NC}"
ssh -t $USER@$DESTINATION "sudo chmod 644 /lib/systemd/system/python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}✅ python-blinds.service permissions set${NC}"

echo -e "${BLUE}🔃 Restarting systemd...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl daemon-reload" > /dev/null 2>&1 && echo -e "${GREEN}✅ systemd daemon reloaded${NC}"

echo -e "${BLUE}🛠️  Ensuring uv is installed on the target...${NC}"
ssh -t $USER@$DESTINATION "command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh" > /dev/null 2>&1 && echo -e "${GREEN}✅ uv is available${NC}"

echo -e "${BLUE}🐍 Syncing Python dependencies with uv...${NC}"
ssh -t $USER@$DESTINATION "export PATH=\"\$HOME/.local/bin:\$PATH\" && cd $REMOTE_ROOT && uv sync --project blinds --locked --no-dev" > /dev/null 2>&1 && echo -e "${GREEN}✅ Python dependencies synced${NC}"

echo -e "${BLUE}▶️  Restarting python-blinds service...${NC}"
ssh -t $USER@$DESTINATION "sudo systemctl restart python-blinds.service" > /dev/null 2>&1 && echo -e "${GREEN}✅ python-blinds.service restarted${NC}"