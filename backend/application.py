from flask import Flask, request, jsonify
from flask_cors import CORS

application = Flask(__name__)
CORS(application) # Handles all permissions

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    # This function will now succeed
    print("✅ JOIN TEAM ROUTE WAS SUCCESSFULLY CALLED")
    user_data = request.get_json()
    user_name = user_data.get('name', 'Unknown User')
    return jsonify({
        "message": f"Success! Joined team as {user_name}."
    })