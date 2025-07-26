#!/bin/bash

# ProductivityFlow DMG Installation Script
# Version: 3.1.0
# Date: July 25, 2025

echo "🚀 ProductivityFlow Installation Script"
echo "========================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is designed for macOS only."
    exit 1
fi

# Function to install DMG
install_dmg() {
    local dmg_file="$1"
    local app_name="$2"
    
    if [ ! -f "$dmg_file" ]; then
        echo "❌ Error: $dmg_file not found!"
        return 1
    fi
    
    echo "📦 Installing $app_name..."
    echo "   Mounting DMG: $dmg_file"
    
    # Mount the DMG
    hdiutil attach "$dmg_file" -quiet
    
    # Find the mounted volume
    local volume_path=$(hdiutil info | grep "/Volumes/" | tail -1 | awk '{print $3}')
    
    if [ -z "$volume_path" ]; then
        echo "❌ Error: Could not mount DMG"
        return 1
    fi
    
    echo "   Volume mounted at: $volume_path"
    
    # Find the .app file
    local app_path=$(find "$volume_path" -name "*.app" -type d | head -1)
    
    if [ -z "$app_path" ]; then
        echo "❌ Error: No .app file found in DMG"
        hdiutil detach "$volume_path" -quiet
        return 1
    fi
    
    echo "   Found app: $app_path"
    
    # Copy to Applications
    echo "   Copying to Applications..."
    cp -R "$app_path" "/Applications/"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Successfully installed to /Applications/"
    else
        echo "   ❌ Failed to copy to Applications"
        hdiutil detach "$volume_path" -quiet
        return 1
    fi
    
    # Unmount the DMG
    hdiutil detach "$volume_path" -quiet
    echo "   DMG unmounted"
    
    return 0
}

# Main installation
echo "🔍 Checking for DMG files..."

# Check for Employee Tracker
if [ -f "ProductivityFlow-Employee-Tracker-v3.1.0-FINAL.dmg" ]; then
    echo "✅ Found Employee Tracker DMG"
    install_employee=true
else
    echo "❌ Employee Tracker DMG not found"
    install_employee=false
fi

# Check for Manager Dashboard
if [ -f "ProductivityFlow-Manager-Dashboard-v3.1.0-FINAL.dmg" ]; then
    echo "✅ Found Manager Dashboard DMG"
    install_manager=true
else
    echo "❌ Manager Dashboard DMG not found"
    install_manager=false
fi

echo ""

# Install applications
if [ "$install_employee" = true ]; then
    install_dmg "ProductivityFlow-Employee-Tracker-v3.1.0-FINAL.dmg" "Employee Activity Tracker"
    echo ""
fi

if [ "$install_manager" = true ]; then
    install_dmg "ProductivityFlow-Manager-Dashboard-v3.1.0-FINAL.dmg" "Manager Dashboard"
    echo ""
fi

echo "🎉 Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Open Applications folder"
echo "   2. Launch the installed apps"
echo "   3. Follow the setup instructions"
echo ""
echo "🔗 Backend Status: https://my-home-backend-7m6d.onrender.com/health"
echo "📚 Documentation: See README.md for detailed instructions"
echo ""
echo "✨ Thank you for using ProductivityFlow!" 