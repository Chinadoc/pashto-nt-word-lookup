import os
import json
import requests
from flask import Flask, request, render_template, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Load NT word index at startup
with open(os.path.join(os.path.dirname(__file__), 'nt_word_index.json'), encoding='utf-8') as f:
    WORD_INDEX = json.load(f)

def fetch_lingdocs(word):
    # Try to fetch the dictionary entry from Lingdocs
    url = f"https://dictionary.lingdocs.com/search/{word}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return "No dictionary entry found."
    soup = BeautifulSoup(resp.text, "html.parser")
    # Try to extract the main entry (this may need adjustment if Lingdocs changes layout)
    entry = soup.find(class_="entry-container")
    if entry:
        return str(entry)
    # Fallback: extract the main content
    main = soup.find("main")
    if main:
        return str(main)
    return "No dictionary entry found."

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    verses = []
    word = ""
    if request.method == "POST":
        word = request.form.get("word", "").strip()
        # Dictionary lookup
        result = fetch_lingdocs(word)
        # NT verses lookup
        verses = WORD_INDEX.get(word, [])
    return render_template("index.html", word=word, result=result, verses=verses)

@app.route("/api/lookup")
def api_lookup():
    word = request.args.get("word", "").strip()
    result = fetch_lingdocs(word)
    verses = WORD_INDEX.get(word, [])
    return jsonify({"dictionary": result, "verses": verses})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
