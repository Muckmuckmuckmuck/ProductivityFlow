#!/usr/bin/env python3
"""
ProductivityFlow Update Server
Simple update server for the auto-updater system
"""

import os
import json
import hashlib
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Update server configuration
UPDATES_DIR = "updates"
CURRENT_VERSION = "1.0.0"

# Ensure updates directory exists
os.makedirs(UPDATES_DIR, exist_ok=True)

@app.route('/api/updates/check/<platform>/<current_version>', methods=['GET'])
def check_for_updates(platform, current_version):
    """Check for available updates"""
    try:
        # Get latest version info
        latest_version = get_latest_version(platform)
        
        if latest_version and latest_version['version'] != current_version:
            return jsonify({
                'update_available': True,
                'current_version': current_version,
                'latest_version': latest_version['version'],
                'download_url': latest_version['download_url'],
                'release_notes': latest_version['release_notes'],
                'file_size': latest_version['file_size'],
                'checksum': latest_version['checksum']
            })
        else:
            return jsonify({
                'update_available': False,
                'current_version': current_version,
                'latest_version': current_version
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates/download/<platform>/<version>', methods=['GET'])
def download_update(platform, version):
    """Download update file"""
    try:
        update_file = os.path.join(UPDATES_DIR, f"productivityflow_{platform}_{version}.zip")
        
        if os.path.exists(update_file):
            return send_file(update_file, as_attachment=True)
        else:
            return jsonify({'error': 'Update file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates/latest/<platform>', methods=['GET'])
def get_latest_update(platform):
    """Get latest update information"""
    try:
        latest = get_latest_version(platform)
        if latest:
            return jsonify(latest)
        else:
            return jsonify({'error': 'No updates available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_latest_version(platform):
    """Get latest version information for platform"""
    # This would typically read from a database or file
    # For now, return hardcoded data
    if platform == "macos":
        return {
            'version': '1.0.1',
            'platform': 'macos',
            'download_url': f'/api/updates/download/macos/1.0.1',
            'release_notes': 'Bug fixes and performance improvements',
            'file_size': 52428800,  # 50MB
            'checksum': 'abc123def456',
            'release_date': datetime.now().isoformat()
        }
    elif platform == "windows":
        return {
            'version': '1.0.1',
            'platform': 'windows',
            'download_url': f'/api/updates/download/windows/1.0.1',
            'release_notes': 'Bug fixes and performance improvements',
            'file_size': 52428800,  # 50MB
            'checksum': 'abc123def456',
            'release_date': datetime.now().isoformat()
        }
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ProductivityFlow Update Server',
        'version': CURRENT_VERSION,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting ProductivityFlow Update Server...")
    print(f"📁 Updates directory: {os.path.abspath(UPDATES_DIR)}")
    print(f"🌐 Server will run on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 