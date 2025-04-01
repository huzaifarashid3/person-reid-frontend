from flask import Blueprint, request, jsonify, send_from_directory
from .video_processor import VideoProcessor
from .person_reid import PersonReID
from .config import Config
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)
video_processor = VideoProcessor()
person_reid = PersonReID()

@main.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        if 'video' not in request.files:
            logger.error('No video file provided')
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        logger.info(f'Processing video: {video_file.filename}')
        # Process video and extract frames with objects
        video_data = video_processor.process_video(video_file)
        return jsonify(video_data)
    except Exception as e:
        logger.error(f'Error processing video: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/api/add-target', methods=['POST'])
def add_target():
    try:
        data = request.json
        if not data:
            logger.error('No data provided')
            return jsonify({'error': 'No data provided'}), 400

        target_type = data.get('type')  # 'image' or 'text'
        target_data = data.get('data')  # image URL or text description
        target_name = data.get('name')

        if not all([target_type, target_data, target_name]):
            logger.error('Missing required fields')
            return jsonify({'error': 'Missing required fields'}), 400

        logger.info(f'Adding target: {target_name} ({target_type})')
        # Add target and generate embeddings
        target_id = person_reid.add_target(target_type, target_data, target_name)
        return jsonify({'target_id': target_id})
    except Exception as e:
        logger.error(f'Error adding target: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/api/search-targets', methods=['POST'])
def search_targets():
    try:
        data = request.json
        if not data:
            logger.error('No data provided')
            return jsonify({'error': 'No data provided'}), 400

        video_ids = data.get('video_ids', [])
        target_ids = data.get('target_ids', [])

        if not video_ids or not target_ids:
            logger.error('Missing video_ids or target_ids')
            return jsonify({'error': 'Missing video_ids or target_ids'}), 400

        logger.info(f'Searching targets {target_ids} in videos {video_ids}')
        # Search for targets in videos
        results = person_reid.search_targets(video_ids, target_ids)
        return jsonify(results)
    except Exception as e:
        logger.error(f'Error searching targets: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/api/get-results/<video_id>/<target_id>', methods=['GET'])
def get_results(video_id, target_id):
    try:
        logger.info(f'Getting results for video {video_id} and target {target_id}')
        # Retrieve specific results for a video-target pair
        results = person_reid.get_results(video_id, target_id)
        return jsonify(results)
    except Exception as e:
        logger.error(f'Error getting results: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/processed/<path:filename>')
def serve_processed_frame(filename):
    """Serve processed frames from the processed directory."""
    return send_from_directory(Config.PROCESSED_FOLDER, filename) 

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})