#!/bin/bash

# Styling definitions
BOLD='\033[1m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m' # No Color

clear
echo -e "${BOLD}${CYAN}=================================================="
echo -e "   LearnOnline Container Orchestration Launcher   "
echo -e "==================================================${NC}"
echo -e "This script simplifies Docker environment launches."
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${BOLD}${RED}ERROR: Docker daemon is not running!${NC}"
    echo -e "Please start Docker Desktop on your macOS and try again."
    exit 1
fi

echo -e "${BOLD}Select Environment to Launch:${NC}"
echo -e "  ${BOLD}${GREEN}1)${NC} Development Mode (Hot-reload, single Redis, DB)"
echo -e "  ${BOLD}${CYAN}2)${NC} Production Simulation Mode (Nginx HTTPS, Gunicorn, multi-worker)"
echo -e "  ${BOLD}${RED}3)${NC} Shutdown & Cleanup (Stop containers, clear volumes)"
echo -e "  ${BOLD}${YELLOW}4)${NC} Cancel & Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "\n${BOLD}${GREEN}[+] Launching Local Development Environment...${NC}"
        docker compose -f docker/docker-compose.yml up --build -d
        echo -e "\n${BOLD}${GREEN}✔ Development containers started successfully!${NC}"
        echo -e "👉 Access URL: ${BOLD}${CYAN}http://localhost:8000${NC}"
        echo -e "👉 Admin Panel: ${BOLD}${CYAN}http://localhost:8000/admin/${NC}"
        ;;
    2)
        # Ensure self-signed certificate exists for HTTPS to prevent Nginx crash
        if [ ! -f docker/nginx/certs/server.crt ]; then
            echo -e "\n${BOLD}${YELLOW}[!] SSL certificates missing. Generating self-signed keys...${NC}"
            mkdir -p docker/nginx/certs
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout docker/nginx/certs/server.key \
                -out docker/nginx/certs/server.crt \
                -subj "/C=VN/ST=Hanoi/L=Hanoi/O=LearnOnline/OU=IT/CN=localhost" >/dev/null 2>&1
            echo -e "${BOLD}${GREEN}✔ SSL keys generated successfully!${NC}"
        fi

        echo -e "\n${BOLD}${CYAN}[+] Launching Production Simulation Environment...${NC}"
        docker compose -f docker/docker-compose.prod.yml up --build -d
        echo -e "\n${BOLD}${CYAN}✔ Production simulation containers started successfully!${NC}"
        echo -e "👉 Access URL: ${BOLD}${CYAN}https://localhost${NC} (Accept self-signed certificate)"
        echo -e "👉 Admin Panel: ${BOLD}${CYAN}https://localhost/admin/${NC}"
        echo -e "\n${BOLD}${YELLOW}💡 Note:${NC} You can run Locust load testing locally using:"
        echo -e "   ${BOLD}uv run locust --headless --users 2000 --spawn-rate 50 --run-time 60s --host https://localhost${NC}"
        ;;
    3)
        echo -e "\n${BOLD}${RED}[-] Shutting down all active container setups...${NC}"
        docker compose -f docker/docker-compose.yml down -v
        docker compose -f docker/docker-compose.prod.yml down -v
        echo -e "\n${BOLD}${GREEN}✔ Cleanup completed successfully. All volumes and containers deleted!${NC}"
        ;;
    *)
        echo -e "\n${BOLD}${YELLOW}Execution cancelled. Bye!${NC}"
        exit 0
        ;;
esac
