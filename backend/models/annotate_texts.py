from flask import Flask, jsonify, request
from flask_cors import CORS

app: Flask = Flask(__name__)
CORS(app)


@app.route("/api/annotate/<model_type>", methods=["POST"])
def get_annotation(model_type):
    try:
        data = request.get_json()
        docs = data.get("docs", [])

        model = model_selection(model_type)
        annotation = annotate(docs, model, model_type)

        return jsonify({"annotation": annotation}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def test():
    return jsonify({"message": "Success"}), 200


def model_selection(model_type):
    if model_type == "matscholar":
        from lbnlp.models.load.matscholar_2020v1 import load

        ner_model = load("ner")
    elif model_type == "matbert":
        from lbnlp.models.load.matbert_ner_2021v1 import load

        ner_model = load("solid_state")
    elif model_type == "relevance":
        from lbnlp.models.load.relevance_2020v1 import load

        ner_model = load("relevance")

    return ner_model


def annotate(docs, model, model_type):
    if model_type == "matscholar":
        tags = [model.tag_doc(doc) for doc in docs]
    elif model_type == "matbert":
        tags = model.tag_docs(docs)
    elif model_type == "relevance":
        tags = model.classify_many(docs)

    return tags


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
