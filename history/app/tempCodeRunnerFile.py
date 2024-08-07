# Path to the folders containing images
HISTORY_FOLDER = os.path.join(app.root_path, 'history')
TEST_FOLDER = os.path.join(app.root_path, 'test')
SEGMENTS_FOLDER = os.path.join(app.root_path, 'segments')

@app.route('/images', methods=['GET'])
def list_images():
    images = []
    for folder in [HISTORY_FOLDER, TEST_FOLDER]:
        folder_name = 'history' if folder == HISTORY_FOLDER else 'test'
        for filename in os.listdir(folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(folder, filename)
                file_info = os.stat(file_path)
                modification_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%d/%m/%Y')
                images.append({'filename': filename, 'date': modification_time, 'folder': folder_name, 'path': f'/images/{folder_name}/{filename}'})
    
    for subdir in os.listdir(SEGMENTS_FOLDER):
        subdir_path = os.path.join(SEGMENTS_FOLDER, subdir)
        if os.path.isdir(subdir_path):
            for filename in os.listdir(subdir_path):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(subdir_path, filename)
                    file_info = os.stat(file_path)
                    modification_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%d/%m/%Y')
                    images.append({'filename': filename, 'date': modification_time, 'folder': 'segments', 'subfolder': subdir, 'path': f'/images/segments/{subdir}/{filename}'})
    
    print(images)
    return jsonify(images)

@app.route('/images/<folder>/<filename>', methods=['GET'])
@app.route('/images/<folder>/<subfolder>/<filename>', methods=['GET'])
def get_image(folder, filename, subfolder=None):
    if subfolder:
        folder_path = os.path.join(app.root_path, folder, subfolder)
    else:
        folder_path = os.path.join(app.root_path, folder)
    
    if os.path.exists(os.path.join(folder_path, filename)):
        return send_from_directory(folder_path, filename)
    else:
        return "File not found", 404