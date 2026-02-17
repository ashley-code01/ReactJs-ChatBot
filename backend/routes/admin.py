"""
Admin routes - Statistics and management
"""

from flask import Blueprint, jsonify
from models import get_session, Conversation, Message, TrainingDocument, UserPreference
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    try:
        db = get_session()
        
        # Count totals
        total_conversations = db.query(Conversation).count()
        total_messages = db.query(Message).count()
        total_users = db.query(Conversation.user_id).distinct().count()
        total_documents = db.query(TrainingDocument).count()
        
        # Feedback stats
        positive_feedback = db.query(Message).filter_by(feedback='positive').count()
        negative_feedback = db.query(Message).filter_by(feedback='negative').count()
        
        # Recent activity
        recent_conversations = db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).limit(5).all()
        
        recent_activity = [{
            'session_id': conv.session_id,
            'updated_at': conv.updated_at.isoformat(),
            'message_count': len(conv.messages)
        } for conv in recent_conversations]
        
        db.close()
        
        return jsonify({
            'success': True,
            'statistics': {
                'conversations': total_conversations,
                'messages': total_messages,
                'users': total_users,
                'training_documents': total_documents,
                'feedback': {
                    'positive': positive_feedback,
                    'negative': negative_feedback,
                    'total': positive_feedback + negative_feedback
                }
            },
            'recent_activity': recent_activity
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@admin_bp.route('/feedback/summary', methods=['GET'])
def feedback_summary():
    """Get detailed feedback summary"""
    try:
        db = get_session()
        
        # Get messages with feedback
        messages_with_feedback = db.query(Message).filter(
            Message.feedback.isnot(None)
        ).all()
        
        feedback_data = [{
            'id': msg.id,
            'feedback': msg.feedback,
            'comment': msg.feedback_comment,
            'message_preview': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'source': msg.source
        } for msg in messages_with_feedback]
        
        db.close()
        
        return jsonify({
            'success': True,
            'feedback_entries': feedback_data,
            'total': len(feedback_data)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500