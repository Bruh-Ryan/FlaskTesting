from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit, join_room, leave_room
import uuid
import random
import string

dashboard = Blueprint('dashboard', __name__, url_prefix='/dash_board')
active_sessions = {}  # Store active sessions with session_id as key

def generate_session_id(length=6):
    """Generate a simple alphanumeric session ID"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@dashboard.route('/')
def dashboard_homepage():
    return render_template('dashboard_page.html')

@dashboard.route('/create-session', methods=['POST'])
def create_session():
    """Create a new examination session"""
    session_id = generate_session_id()
    # Store session info
    active_sessions[session_id] = {
        'examiner': None,
        'attendee': None
    }
    return jsonify({'session_id': session_id})

@dashboard.route('/check-session/<session_id>')
def check_session(session_id):
    """Check if a session exists"""
    if session_id in active_sessions:
        return jsonify({'exists': True})
    return jsonify({'exists': False})

# This function will be called from your main app to register socket handlers
def register_socket_events(socketio):
    @socketio.on('join_session', namespace='/dashboard')
    def handle_join_session(data):
        user_id = str(uuid.uuid4())
        session_id = data.get('session_id')
        role = data.get('role')
        
        if not session_id or session_id not in active_sessions:
            emit('error', {'message': 'Invalid session ID'})
            return
        
        # Join the session room
        join_room(session_id)
        join_room(user_id)
        
        # Register user in the session
        if role == 'examiner':
            active_sessions[session_id]['examiner'] = user_id
        else:  # attendee
            active_sessions[session_id]['attendee'] = user_id
        
        # Check if both users are in the session
        session = active_sessions[session_id]
        if session['examiner'] and session['attendee']:
            # Inform both users they're connected
            emit('user_joined', {
                'user_id': user_id,
                'partner_id': session['attendee'] if role == 'examiner' else session['examiner'],
                'role': role
            }, room=user_id)
            
            # Notify the other user about this user joining
            other_id = session['attendee'] if role == 'examiner' else session['examiner']
            emit('user_joined', {
                'user_id': other_id,
                'partner_id': user_id,
                'role': 'attendee' if role == 'examiner' else 'examiner'
            }, room=other_id)
        else:
            # Waiting for the other user
            emit('waiting_for_partner', {
                'session_id': session_id,
                'role': role
            }, room=user_id)
    
    @socketio.on('offer', namespace='/dashboard')
    def handle_offer(data):
        emit('offer', data['offer'], room=data['target'], namespace='/dashboard')
    
    @socketio.on('answer', namespace='/dashboard')
    def handle_answer(data):
        emit('answer', data['answer'], room=data['target'], namespace='/dashboard')
    
    @socketio.on('ice_candidate', namespace='/dashboard')
    def handle_ice_candidate(data):
        emit('ice_candidate', data['candidate'], room=data['target'], namespace='/dashboard')
    
    @socketio.on('disconnect', namespace='/dashboard')
    def handle_disconnect():
        # Remove the user from any active sessions
        for session_id, session in list(active_sessions.items()):
            if session['examiner'] == request.sid:
                session['examiner'] = None
                emit('partner_disconnected', room=session_id)
            elif session['attendee'] == request.sid:
                session['attendee'] = None
                emit('partner_disconnected', room=session_id)
            
            # Clean up empty sessions
            if not session['examiner'] and not session['attendee']:
                del active_sessions[session_id]