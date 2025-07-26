#!/bin/bash

# ProductivityFlow v3.1.0 Installation Script
# This script automates the installation of both Employee Tracker and Manager Dashboard

echo "🚀 ProductivityFlow v3.1.0 Installation Script"
echo "=============================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is designed for macOS only."
    exit 1
fi

# Function to install an application
install_app() {
    local app_name="$1"
    local dmg_file="$2"
    local app_folder="$3"
    
    echo "📦 Installing $app_name..."
    
    # Check if DMG file exists
    if [ ! -f "$dmg_file" ]; then
        echo "❌ Error: $dmg_file not found in current directory"
        return 1
    fi
    
    # Mount the DMG
    echo "   Mounting $dmg_file..."
    hdiutil attach "$dmg_file" -quiet
    
    # Find the mounted volume
    local volume_path=$(hdiutil info | grep "/Volumes/" | tail -1 | awk '{print $3}')
    
    if [ -z "$volume_path" ]; then
        echo "❌ Error: Could not mount DMG file"
        return 1
    fi
    
    # Copy application to Applications folder
    echo "   Copying to Applications folder..."
    cp -R "$volume_path/$app_folder" "/Applications/"
    
    # Unmount the DMG
    echo "   Unmounting DMG..."
    hdiutil detach "$volume_path" -quiet
    
    # Check if installation was successful
    if [ -d "/Applications/$app_folder" ]; then
        echo "✅ $app_name installed successfully!"
        return 0
    else
        echo "❌ Error: Failed to install $app_name"
        return 1
    fi
}

# Install Employee Tracker
echo "1️⃣ Installing Employee Tracker..."
install_app "Employee Tracker" "ProductivityFlow-Employee-Tracker-v3.1.0.dmg" "ProductivityFlow Employee Tracker v3.1.0.app"

echo ""

# Install Manager Dashboard
echo "2️⃣ Installing Manager Dashboard..."
install_app "Manager Dashboard" "ProductivityFlow-Manager-Dashboard-v3.1.0.dmg" "ProductivityFlow Manager Dashboard v3.1.0.app"

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Open Applications folder"
echo "   2. Launch 'ProductivityFlow Employee Tracker' to start tracking"
echo "   3. Launch 'ProductivityFlow Manager Dashboard' to manage your team"
echo ""
echo "💡 Tip: You can also use Spotlight (Cmd+Space) to quickly find the apps"
echo ""
echo "🔗 For support, refer to the README.md file in this directory" 