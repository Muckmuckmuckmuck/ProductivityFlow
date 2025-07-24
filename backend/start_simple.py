#!/usr/bin/env python3
import os
from application import application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False) 