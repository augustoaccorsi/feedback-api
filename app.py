from flask import Flask, jsonify,abort, make_response, request, url_for
import os
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)
port = int(os.getenv("PORT", 9099))

feedbacks = [
    {
        'id': 1,
        'component': 'COMPONENT-A',
        'rate': 1,
        'description': "bad response time"
    },
    {
        'id': 2,
        'component': 'COMPONENT-B',
        'rate': 5,
        'description': "awesome feedback service"
    }
]

def make_public_feedback(feedback):
    new_feedback = {}
    for field in feedback:
        if field == 'id':
            new_feedback['uri'] = url_for('get_feedback', feedback_id=feedback['id'], _external=True)
        else:
            new_feedback[field] = feedback[field]
    return new_feedback

@app.route('/feedin/api/v1.0/feedbacks', methods=['GET'])
@auth.login_required
def get_feedbacks():
    return jsonify({'feedbacks': [make_public_feedback(feedback) for feedback in feedbacks]})
    #return jsonify({'feedbacks': feedbacks})

@app.route('/feedin/api/v1.0/feedbacks/<int:feedback_id>', methods=['GET'])
@auth.login_required
def get_feedback(feedback_id):
    feedback = [feedback for feedback in feedbacks if feedback['id'] == feedback_id]
    if len(feedback) == 0:
        abort(404)
    return jsonify({'feedbacks': [make_public_feedback(feedback[0])]})
    #return jsonify({'feedback': feedback[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Feedback not found'}), 404)

@app.route('/feedin/api/v1.0/feedbacks', methods=['POST'])
@auth.login_required
def create_feedback():
    if not request.json or not 'component' in request.json:
        abort(400)
    feedback = {
        'id': feedbacks[-1]['id'] + 1,
        'component': request.json['component'],
        'rate': request.json['rate'],
        'description': request.json.get('description', ""),
    }
    feedbacks.append(feedback)
    #return jsonify({'feedback': feedback}), 201
    return jsonify({'feedback': [make_public_feedback(feedback)]}), 201

@app.route('/feedin/api/v1.0/feedbacks/<int:feedback_id>', methods=['PUT'])
@auth.login_required
def update_feedback(feedback_id):
    feedback = [feedback for feedback in feedbacks if feedback['id'] == feedback_id]
    if len(feedback) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'component' in request.json and type(request.json['component']) is int:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is int:
        abort(400)
    if 'rate' in request.json and type(request.json['rate']) is not int:
        abort(400)
    feedback[0]['component'] = request.json.get('component', feedback[0]['component'])
    feedback[0]['description'] = request.json.get('description', feedback[0]['description'])
    feedback[0]['rate'] = request.json.get('rate', feedback[0]['rate'])
    #return jsonify({'feedback': feedback[0]})
    return jsonify({'feedback': [make_public_feedback(feedback[0])]})

@app.route('/feedin/api/v1.0/feedbacks/<int:feedback_id>', methods=['DELETE'])
@auth.login_required
def delete_feedback(feedback_id):
    feedback = [feedback for feedback in feedbacks if feedback['id'] == feedback_id]
    if len(feedback) == 0:
        abort(404)
    feedbacks.remove(feedback[0])
    return jsonify({'result': True})

@auth.get_password
def get_password(username):
    if username == 'guto':
        return 'guto'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
    #app.run(debug=True)
