import dotenv
from flask import Flask, request, jsonify
from embeddings import save_embeddings, get_thread_id, retrieve_embeddings
from rag import respond_to_message

app = Flask(__name__)

thread_to_asset_map = {}


@app.route('/api/document/process', methods=['POST'])
def process():
    request_data = request.get_json()

    file_path = request_data.get("file_path", None)
    if file_path is None:
        return jsonify(error="file_path is required"), 400

    asset_id = save_embeddings(file_path)
    return jsonify(asset_id=asset_id), 200


@app.route('/api/chat/start', methods=['POST'])
def start():
    request_data = request.get_json()
    asset_id = request_data.get("asset_id", None)
    if asset_id is None:
        return jsonify(error="asset_id is required"), 400

    embs = retrieve_embeddings(asset_id)
    if embs is None:
        return jsonify(error="Invalid asset_id, no embeddings exists for it"), 404

    thread_id = get_thread_id()
    thread_to_asset_map[thread_id] = asset_id

    return jsonify(thread_id=thread_id), 200


@app.route('/api/chat/message', methods=['POST'])
def message():
    request_data = request.get_json()
    thread_id = request_data.get("thread_id", None)
    if thread_id is None:
        return jsonify(error="thread_id is required"), 400
    user_message = request_data.get("user_message", None)
    if user_message is None:
        return jsonify(error="user_message is required"), 400

    
    asset_id = thread_to_asset_map.get(thread_id, None)
    if asset_id is None:
        return jsonify(error="Invalid chat-thread id, create a new one"), 404
    result = respond_to_message(user_message, asset_id)
    print(result)
    return jsonify(msg=result)


@app.route('/api/chat/history', methods=['GET'])
def history():
    request_data = request.get_json()
    thread_id = request_data.get("thread_id", None)
    if thread_id is None:
        return jsonify(error="thread_id is required"), 400


if __name__ == '__main__':
    dotenv.load_dotenv()
    # print(respond_to_message("Hi, explain this doc", "70c81f8e-b2a2-4e54-9a34-c71c6d206d72"))
    app.run(debug=True)
