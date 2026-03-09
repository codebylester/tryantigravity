import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agent.sql_agent import SQLAgent

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow frontend to talk to backend

# Initialize our SQL Agent
agent_init_error = None
try:
    agent = SQLAgent(schema_dir="schemas")
except Exception as e:
    print(f"Error initializing SQL Agent: {e}")
    agent_init_error = str(e)
    agent = None

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/generate', methods=['POST'])
def generate_sql():
    """API endpoint to generate SQL from text."""
    if not agent:
        error_msg = f"SQL Agent not initialized: {agent_init_error}" if agent_init_error else "SQL Agent not initialized"
        return jsonify({"error": error_msg}), 500

    data = request.json
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        sql = agent.generate_query(user_question)
        return jsonify({
            "question": user_question,
            "sql": sql
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """API endpoint to get the current schema text."""
    if not agent:
        return jsonify({"error": "SQL Agent not initialized"}), 500
    return jsonify({"schema": agent.get_schema()})

@app.route('/api/upload-schema', methods=['POST'])
def upload_schema():
    """API endpoint to update the schema from a .sql file."""
    if not agent:
        return jsonify({"error": "SQL Agent not initialized"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = file.filename.lower()
    try:
        content = file.read().decode('utf-8')
        
        # Smart detection: Does it already contain SQL CREATE statements?
        is_sql_already = "CREATE TABLE" in content.upper()

        if is_sql_already:
            # It's SQL, skip inference even if it's a .csv file
            schema_content = content
        elif filename.endswith('.csv'):
            # It's raw data, use Gemini to build a table schema for it
            schema_content = agent.infer_schema_from_csv(content, file.filename)
        elif filename.endswith('.sql'):
            # Standard SQL file
            schema_content = content
        else:
            return jsonify({"error": "File type not supported. Please use .sql or .csv"}), 400

        agent.set_schema(schema_content)
        return jsonify({
            "message": "Schema updated successfully",
            "filename": file.filename,
            "type": "SQL Detection" if is_sql_already else "AI Inference" if filename.endswith('.csv') else "Direct SQL"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use the PORT environment variable assigned by the cloud provider
    # Default to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
