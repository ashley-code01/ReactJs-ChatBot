"""
Chat routes - Handle conversation logic
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from models import get_session, Conversation, Message

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/message', methods=['POST'])
def handle_message():
    """
    Handle incoming chat messages
    
    Expected JSON:
    {
        "message": "message text",
        "session_id": "optional-session-id",
        "user_id": "optional-user-id",
        "role": "user" or "assistant" (optional, defaults to "user"),
        "source": "where message came from" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message_content = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_id = data.get('user_id')
        role = data.get('role', 'user')  # Default to 'user' if not specified
        source = data.get('source', 'user_input' if role == 'user' else 'unknown')
        
        # Validate role
        if role not in ['user', 'assistant']:
            return jsonify({'error': 'Role must be "user" or "assistant"'}), 400
        
        # Get or create session
        db = get_session()
        conversation = db.query(Conversation).filter_by(session_id=session_id).first()
        
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id
            )
            db.add(conversation)
            db.commit()
        
        # Save message
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=message_content,
            source=source
        )
        db.add(message)
        db.commit()
        
        message_id = message.id
        db.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message_id': message_id,
            'message': 'Message saved successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        db = get_session()
        conversation = db.query(Conversation).filter_by(session_id=session_id).first()
        
        if not conversation:
            return jsonify({'error': 'Session not found'}), 404
        
        messages = [{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'source': msg.source,
            'feedback': msg.feedback
        } for msg in conversation.messages]
        
        db.close()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'messages': messages,
            'message_count': len(messages)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@chat_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for a message
    
    Expected JSON:
    {
        "message_id": 123,
        "feedback": "positive" or "negative",
        "comment": "optional comment"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message_id' not in data or 'feedback' not in data:
            return jsonify({'error': 'message_id and feedback are required'}), 400
        
        message_id = data['message_id']
        feedback = data['feedback']
        comment = data.get('comment')
        
        if feedback not in ['positive', 'negative']:
            return jsonify({'error': 'feedback must be "positive" or "negative"'}), 400
        
        db = get_session()
        message = db.query(Message).filter_by(id=message_id).first()
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        message.feedback = feedback
        message.feedback_comment = comment
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@chat_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all conversation sessions"""
    try:
        db = get_session()
        conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        
        sessions = [{
            'session_id': conv.session_id,
            'user_id': conv.user_id,
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat(),
            'message_count': len(conv.messages)
        } for conv in conversations]
        
        db.close()
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500