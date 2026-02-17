"""
Training routes - Handle document uploads and training
(Phase 2 - will be fully implemented later)
"""

from flask import Blueprint, request, jsonify
from models import get_session, TrainingDocument
from datetime import datetime

training_bp = Blueprint('training', __name__)


@training_bp.route('/status', methods=['GET'])
def training_status():
    """Get training system status"""
    try:
        db = get_session()
        total_docs = db.query(TrainingDocument).count()
        processed_docs = db.query(TrainingDocument).filter_by(processed=True).count()
        db.close()
        
        return jsonify({
            'success': True,
            'total_documents': total_docs,
            'processed_documents': processed_docs,
            'pending_documents': total_docs - processed_docs,
            'status': 'ready'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@training_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload a training document
    (Placeholder - will implement file upload in Phase 2)
    """
    return jsonify({
        'success': False,
        'message': 'Document upload will be implemented in Phase 2',
        'phase': 'coming_soon'
    }), 501


@training_bp.route('/documents', methods=['GET'])
def list_documents():
    """List all training documents"""
    try:
        db = get_session()
        documents = db.query(TrainingDocument).order_by(TrainingDocument.uploaded_at.desc()).all()
        
        docs_list = [{
            'id': doc.id,
            'title': doc.title,
            'file_type': doc.file_type,
            'category': doc.category,
            'processed': doc.processed,
            'chunk_count': doc.chunk_count,
            'uploaded_at': doc.uploaded_at.isoformat()
        } for doc in documents]
        
        db.close()
        
        return jsonify({
            'success': True,
            'documents': docs_list,
            'total': len(docs_list)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500