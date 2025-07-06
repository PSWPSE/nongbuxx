#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'NONGBUXX Backend is running!',
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-test',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'port': os.getenv('PORT', '5000')
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """테스트 엔드포인트"""
    return jsonify({
        'message': 'Test endpoint working!',
        'environment_variables': {
            'PORT': os.getenv('PORT'),
            'DEBUG': os.getenv('DEBUG'),
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'OPENAI_API_KEY': 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT_SET',
            'ANTHROPIC_API_KEY': 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT_SET'
        }
    })

if __name__ == '__main__':
    # 환경 변수 확인
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting NONGBUXX Test API server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise 