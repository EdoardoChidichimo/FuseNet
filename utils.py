from openai import OpenAI
import spacy
import os

def generate_llm_response(context):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Generate a message relevant to the given context."},
                  {"role": "user", "content": context}]
    )
    return response.choices[0].message.content 


def violent(text, nlp):
    violence_keywords = ["kill", "attack", "destroy", "war", "hate", "murder"]

def kinship(text, nlp):
    KINSHIP_WORDS = set([
        "family", "families", "kin", "kinship", "relatives", "ancestors", "descendants",
        "father", "dad", "daddy", "papa", "pa", "grandfather", "granddad", "grandpa",
        "mother", "mom", "mommy", "mama", "mum", "grandmother", "grandma", "granny", "nana",
        "parent", "parents", "child", "children", "son", "daughter", "sibling", "siblings",
        "brother", "bro", "bros", "sister", "sis", "cousin", "cousins", "aunt", "aunty", "uncle",
        "nephew", "niece", "husband", "wife", "spouse", "partner",
        "grandson", "granddaughter", "stepfather", "stepmother", "stepbrother", "stepsister",
        "godfather", "godmother", "godbrother", "godsister", "godson", "goddaughter"
    ])

    doc = nlp(text)
    return doc.similarity(nlp(" ".join(KINSHIP_WORDS)))  # Compute similarity


def deadly_cocktail_strength(message):

    nlp = spacy.load("en_core_web_md")

    # violence_score = violent(message, nlp)
    kinship_score = kinship(message, nlp)

    return kinship_score