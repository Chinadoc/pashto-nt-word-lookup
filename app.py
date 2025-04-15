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
    print(resp.text)  # Debug: print the HTML response from Lingdocs
    if resp.status_code != 200:
        return "No dictionary entry found."
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find the first link to a word entry
    link = soup.find('a', href=True)
    if link and '/word?id=' in link['href']:
        word_url = f"https://dictionary.lingdocs.com{link['href']}"
        word_resp = requests.get(word_url)
        print(word_resp.text)  # Debug: print the HTML of the word entry page
        if word_resp.status_code == 200:
            word_soup = BeautifulSoup(word_resp.text, "html.parser")
            entry = word_soup.find(class_="entry-container")
            if entry:
                return str(entry)
            main = word_soup.find("main")
            if main:
                return str(main)
        return "No dictionary entry found."
    # If no link found, fallback to old method
    entry = soup.find(class_="entry-container")
    if entry:
        return str(entry)
    main = soup.find("main")
    if main:
        return str(main)
    return "No dictionary entry found."

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    verses = []
    word = ""
    similar_keys = []
    if request.method == "POST":
        word = request.form.get("word", "").strip()
        result = fetch_lingdocs(word)
        # Find exact matches for verses
        verses = WORD_INDEX.get(word, [])
        # Debug: print similar keys in the index
        for k in WORD_INDEX:
            if word in k or k in word:
                similar_keys.append(k)
        print(f"Similar keys for '{word}': {similar_keys}")
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
