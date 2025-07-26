#!/bin/bash

# ProductivityFlow Robust Installation Script
# This script helps install both the Employee Tracker and Manager Dashboard apps

echo "🚀 ProductivityFlow Robust Installation Script"
echo "=============================================="
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only."
    exit 1
fi

# Function to install app from DMG
install_app() {
    local dmg_file="$1"
    local app_name="$2"
    
    echo "📦 Installing $app_name..."
    
    if [ ! -f "$dmg_file" ]; then
        echo "❌ DMG file not found: $dmg_file"
        return 1
    fi
    
    # Mount the DMG
    echo "   Mounting DMG..."
    hdiutil attach "$dmg_file" -quiet
    
    # Find the mounted volume
    local volume_name=$(hdiutil info | grep "/Volumes/" | tail -1 | awk '{print $3}')
    
    if [ -z "$volume_name" ]; then
        echo "❌ Failed to mount DMG"
        return 1
    fi
    
    # Find the .app file
    local app_path=$(find "$volume_name" -name "*.app" -type d | head -1)
    
    if [ -z "$app_path" ]; then
        echo "❌ No .app file found in DMG"
        hdiutil detach "$volume_name" -quiet
        return 1
    fi
    
    # Copy to Applications
    echo "   Copying to Applications..."
    cp -R "$app_path" "/Applications/"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ $app_name installed successfully!"
    else
        echo "   ❌ Failed to install $app_name"
        hdiutil detach "$volume_name" -quiet
        return 1
    fi
    
    # Unmount the DMG
    echo "   Unmounting DMG..."
    hdiutil detach "$volume_name" -quiet
    
    return 0
}

# Function to check if app is already installed
check_installed() {
    local app_name="$1"
    if [ -d "/Applications/$app_name.app" ]; then
        echo "   ⚠️  $app_name is already installed"
        read -p "   Do you want to replace it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Removing existing installation..."
            rm -rf "/Applications/$app_name.app"
            return 0
        else
            return 1
        fi
    fi
    return 0
}

# Main installation process
echo "🔍 Checking for DMG files..."

# Employee Tracker
employee_dmg="ProductivityFlow Employee Tracker v3.1.0_3.1.0_x64.dmg"
if [ -f "$employee_dmg" ]; then
    echo "✅ Found Employee Tracker DMG"
    if check_installed "ProductivityFlow Employee Tracker v3.1.0"; then
        install_app "$employee_dmg" "Employee Tracker"
        employee_installed=$?
    else
        employee_installed=1
    fi
else
    echo "❌ Employee Tracker DMG not found"
    employee_installed=1
fi

echo ""

# Manager Dashboard
manager_dmg="ProductivityFlow Manager Dashboard v3.1.0_3.1.0_x64.dmg"
if [ -f "$manager_dmg" ]; then
    echo "✅ Found Manager Dashboard DMG"
    if check_installed "ProductivityFlow Manager Dashboard v3.1.0"; then
        install_app "$manager_dmg" "Manager Dashboard"
        manager_installed=$?
    else
        manager_installed=1
    fi
else
    echo "❌ Manager Dashboard DMG not found"
    manager_installed=1
fi

echo ""
echo "=============================================="
echo "📋 Installation Summary"
echo "=============================================="

if [ $employee_installed -eq 0 ]; then
    echo "✅ Employee Tracker: Installed successfully"
else
    echo "❌ Employee Tracker: Installation failed or skipped"
fi

if [ $manager_installed -eq 0 ]; then
    echo "✅ Manager Dashboard: Installed successfully"
else
    echo "❌ Manager Dashboard: Installation failed or skipped"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Launch the apps from your Applications folder"
echo "2. For Employee Tracker: Enter your team code to start tracking"
echo "3. For Manager Dashboard: Create an account and start managing teams"
echo ""
echo "📚 Documentation: See BUILD_SUMMARY.md for detailed information"
echo "🔗 Backend URL: https://my-home-backend-7m6d.onrender.com"
echo ""

# Check if both apps are now installed
if [ -d "/Applications/ProductivityFlow Employee Tracker v3.1.0.app" ] && [ -d "/Applications/ProductivityFlow Manager Dashboard v3.1.0.app" ]; then
    echo "🎉 Both apps are now installed and ready to use!"
elif [ -d "/Applications/ProductivityFlow Employee Tracker v3.1.0.app" ]; then
    echo "✅ Employee Tracker is installed and ready to use!"
elif [ -d "/Applications/ProductivityFlow Manager Dashboard v3.1.0.app" ]; then
    echo "✅ Manager Dashboard is installed and ready to use!"
else
    echo "⚠️  No apps were installed. Please check the DMG files and try again."
fi

echo ""
echo "🚀 Thank you for using ProductivityFlow!" 