#!/usr/bin/env bash
# This script produces a runnable waifu2x release that should work on your system. If it doesn't, please let me know.

# Requirements...
if ! command -v ffmpeg > /dev/null 2>&1; then
    echo could not find path to ffmpeg binary
    exit
fi

if ! command -v python3 -v > /dev/null 2>&1; then
    echo could not find path to ffmpeg binary
    exit
fi

# Delete and make new folder
rm -rf ./dandere2x_release
mkdir -p ./dandere2x_release

# Delete venv_build if already exists from separate run
rm -rf ./venv_build

# Create venv for building && enter venv
python3 -m venv venv_build
source ./venv_build/bin/activate

# Install requirements needed for building
pip3 install -r requirements.txt

# Build the python binary
pyinstaller -F gui_driver.py

# Copy built pyinstaller driver to dandere2x_release folder
cp ./dist/gui_driver ./dandere2x_release/dandere2x

# Copy needed config_files and gui over to dandere2x_release folder
cp -R ./config_files ./dandere2x_release/config_files
cp -R ./gui ./dandere2x_release/gui

# Download custom waifu2x-ncnn-vulkan
wget https://github.com/akai-katto/waifu2x-ncnn-vulkan-server/releases/download/0.1.3/waifu2x-ncnn-vulkan-0.1.3-ubuntu.zip
mkdir -p ./dandere2x_release/externals/
unzip waifu2x-ncnn-vulkan-0.1.3-ubuntu.zip
rm waifu2x-ncnn-vulkan-0.1.3-ubuntu.zip
mv waifu2x-ncnn-vulkan-0.1.3-ubuntu waifu2x-ncnn-vulkan-server
mv waifu2x-ncnn-vulkan-server/ ./dandere2x_release/externals/

# Download test video and create workspace
wget https://github.com/akai-katto/dandere2x_externals_static/releases/download/0.02/yn_moving.mkv
mkdir ./dandere2x_release//workspace
mv yn_moving.mkv ./dandere2x_release/workspace