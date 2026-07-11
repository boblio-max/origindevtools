#!/bin/bash
set -e

REPO="yourusername/origindevtools"
INSTALL_DIR="/usr/local/bin"
BINARY_NAME="origin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installing Origin CLI...${NC}"

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS="linux";;
    Darwin*)    OS="macos";;
    MINGW*|MSYS*|CYGWIN*)  OS="windows";;
    *)          echo -e "${RED}Unsupported OS: ${OS}${NC}"; exit 1;;
esac

# Detect Architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)   ARCH="x86_64";;
    arm64|aarch64)   ARCH="aarch64";;
    armv7l|armhf)    ARCH="armv7";;
    *)               echo -e "${RED}Unsupported architecture: ${ARCH}${NC}"; exit 1;;
esac

# Set binary name based on OS
if [ "${OS}" = "windows" ]; then
    BINARY_NAME="origin.exe"
fi

# Download URL
DOWNLOAD_URL="https://github.com/${REPO}/releases/latest/download/${BINARY_NAME}"

echo -e "${YELLOW}Detected: ${OS} ${ARCH}${NC}"
echo -e "${YELLOW}Downloading from: ${DOWNLOAD_URL}${NC}"

# Download binary
if [ "${OS}" = "windows" ]; then
    # Windows - download to current directory
    curl -fsSL "${DOWNLOAD_URL}" -o "${BINARY_NAME}"
    echo -e "${GREEN}Downloaded ${BINARY_NAME} to current directory${NC}"
    echo -e "${YELLOW}Move ${BINARY_NAME} to a directory in your PATH to use it globally${NC}"
else
    # Linux/macOS - install to /usr/local/bin
    curl -fsSL "${DOWNLOAD_URL}" | sudo tee "${INSTALL_DIR}/${BINARY_NAME}" > /dev/null
    sudo chmod +x "${INSTALL_DIR}/${BINARY_NAME}"
    echo -e "${GREEN}Installed ${BINARY_NAME} to ${INSTALL_DIR}${NC}"
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}Run 'origin' to get started.${NC}"
