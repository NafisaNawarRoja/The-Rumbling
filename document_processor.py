
import os
import PyPDF2

DOCUMENT_FOLDER = "documents"

def load_documents():
    documents = []

    if not os.path.exists(DOCUMENT_FOLDER):
        return documents

    for filename in os.listdir(DOCUMENT_FOLDER):
        path = os.path.join(DOCUMENT_FOLDER, filename)

        if filename.endswith(".pdf"):
            try:
                reader = PyPDF2.PdfReader(path)

                for page_number, page in enumerate(reader.pages):
                    text = page.extract_text() or ""

                    if text.strip():
                        documents.append({
                            "source": filename,
                            "page": page_number + 1,
                            "text": text
                        })

            except Exception as error:
                print(f"Error reading {filename}: {error}")

        elif filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as file:
                text = file.read()

            documents.append({
                "source": filename,
                "page": 1,
                "text": text
            })

    return documents


def search_documents(question, documents, max_results=3):
    question_words = set(question.lower().split())
    results = []

    for document in documents:
        text = document["text"]
        words = set(text.lower().split())
        score = len(question_words.intersection(words))

        if score > 0:
            results.append((score, document))

    results.sort(key=lambda item: item[0], reverse=True)

    selected = results[:max_results]

    return "\n\n".join(
        f"Source: {doc['source']}, Page: {doc['page']}\n{doc['text'][:3000]}"
        for score, doc in selected
    )
