import json
import logging
from datetime import datetime
import os
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, unset_jwt_cookies, get_jwt_identity
from flask_cors import CORS
from dao.TaskSubmission import TaskSubmission
from dao.Role import authorised_user_role, user_role
from service.LoginUser import LoginUser
from flask_jwt_extended import jwt_required
from view.decorators import require_permission, require_additional_permission_with_access_control
from service.AudioAsr import AudioAsr
import uuid

audio = Blueprint('audio', __name__)

CORS(audio, resources={r"/audio/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})


@audio.route('/ping', methods=['GET', 'OPTIONS'])
def ping():
    return jsonify({'success': True, 'msg': 'pong'})


@audio.route('/asr_pre', methods=['POST', 'OPTIONS'])
def asr_pre_test():
    if request.method == 'OPTIONS':
        return _handle_preflight()
    UPLOAD_FOLDER = 'asr_pre_load'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 获取前端传递的音频文件
    audio_file = request.files.get('audio')
    if audio_file.filename == '':
        return '没有选择文件', 400
    
    # 调用asr_service进行语音识别
    asr_service = AudioAsr()
    uuid4 = uuid.uuid4()
    file_path = os.path.join(UPLOAD_FOLDER, str(uuid4)+'_'+str(audio_file.filename))
    
    # 读取文件
    if audio_file:
        audio_file.save(file_path)
        result = asr_service.get_asr_result(file_path)
        os.remove(file_path)

    else:
        result = "No audio file provided"
        return jsonify({'success': False, 'msg': result}), 400
    return jsonify({'success': True, 'transcription': result})




@audio.route('/asr', methods=['POST', 'OPTIONS'])
@jwt_required()
@require_permission('submit_task')
def asr():
    if request.method == 'OPTIONS':
        return _handle_preflight()
    UPLOAD_FOLDER = 'asr_upload'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 获取前端传递的音频文件
    audio_file = request.files.get('audio')

    if audio_file.filename == '':
        return '没有选择文件', 400

    # 调用asr_service进行语音识别
    asr_service = AudioAsr()
    current_user_id = get_jwt_identity()
    file_path = os.path.join(UPLOAD_FOLDER, str(current_user_id)+'_'+str(audio_file.filename))
    
    # 读取文件
    if audio_file:
        audio_file.save(file_path)
        result = asr_service.get_asr_result(file_path)

    else:
        result = "No audio file provided"
        return jsonify({'success': False, 'msg': result}), 400
    return jsonify({'success': True, 'transcription': result})

    
@audio.route('/save_single_asr', methods=['POST', 'OPTIONS'])
@jwt_required()
@require_permission('submit_task')
def save_single_asr():
    if request.method == 'OPTIONS':
        return _handle_preflight()
    # 获取前端传递的音频文件
    audio_file = request.files.get('audio')
    transcription = request.form.get('transcription')
    asr_result = request.form.get('asr_result')
    task_id = request.form.get('task_id')
    turn_id = request.form.get('turn_id')
    language = request.form.get('language')
    asr_service = AudioAsr()

    UPLOAD_FOLDER = 'transcription_upload'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    current_user_id = get_jwt_identity()

    _currentUser = LoginUser().check_user_with_id(current_user_id)

    # 读取文件
    if audio_file:
        file_path = os.path.join(UPLOAD_FOLDER, str(current_user_id)+'_'+str(audio_file.filename))
        audio_file.save(file_path)
        save_result = asr_service.audio_result_insert(file_path, _currentUser, transcription, asr_result, task_id, turn_id,language)
    else:
        save_result = "No audio file provided"
        return  jsonify({'success': True, 'result': save_result}),400
    return jsonify({'success': True, 'result': save_result})



def _handle_preflight():
    """
    Handles preflight requests for CORS.

    This function is called for OPTIONS requests to any of the routes. It sets the necessary headers for CORS support.
    Sometimes, we need this to support the Safari Browser in a development environment.

    Returns:
        Response: A Flask response object with CORS headers set.
    """

    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response