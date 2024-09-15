from flask import Flask, request, jsonify
from gaph import run_rag_agent
from todo_list import get_todo 

app = Flask(__name__)
messages=[]
@app.route('/query', methods=['POST'])
def rag_endpoint():
    data = request.json
    if 'question' not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400
    
    result = run_rag_agent(data['question'])
    messages.append(data['question'])
    messages.append(result['answer'])
    return jsonify(result)

@app.route('/todo', methods=['GET'])
def todo_endpoint():
    todo_list = get_todo()
    return jsonify({"todo": todo_list})

if __name__ == '__main__':
    app.run(debug=True)