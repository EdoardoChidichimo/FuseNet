import os
import spacy
# import google.generativeai as genai
from openai import OpenAI
# from llamaapi import LlamaAPI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def generate_llm_response(context, llm_model, temperature=0.7):
    """
    Generates a response from the specified LLM model.
    
    Supported models:
    - OpenAI GPT: "gpt-3.5-turbo", "gpt-4"
    - Meta LLaMA: "llama-2", "llama-3" (via `llama-cpp-python`)
    - Google Gemini: "gemini-pro" (via `google-generativeai`)
    - Mistral: "mistral-7b" (via Hugging Face `transformers`)
    - ChatGLM: "chatglm-6b", "chatglm2-6b", "chatglm3-6b" (via Hugging Face)
    - Local Models (e.g., GPT-J, Falcon): Any Hugging Face model
    """

    if "gpt" in llm_model.lower():  # OpenAI GPT Models
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "system", "content": f"You are a social media user."},
                      {"role": "user", "content": context}],
            temperature=temperature
        )
        return response.choices[0].message.content

    elif "llama" in llm_model.lower():  # Meta's LLaMA Models (Local)
        llm = LlamaAPI(os.getenv("LLAMA_API_KEY")) 
        api_request_json = {
            "model": llm_model,  
            "messages": [
                {"role": "user", "content": context}
            ],
            "stream": False  
        }
        response = llm.run(api_request_json)
        return response.json()["choices"][0]["message"]["content"]


    elif "gemini" in llm_model.lower():  # Google's Gemini Models
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(llm_model)  # "gemini-pro"
        response = model.generate_content(context)
        return response.text

    elif "mistral" in llm_model.lower():  # Mistral Models (Hugging Face)
        model_name = "mistralai/Mistral-7B-v0.1"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        output = pipe(context, max_length=100)
        return output[0]["generated_text"]

    elif "chatglm" in llm_model.lower():  # ChatGLM Models (THUDM)
        model_name = "THUDM/chatglm3-6b"  # or "THUDM/chatglm2-6b"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        output = pipe(context, max_length=100)
        return output[0]["generated_text"]

    else:
        raise ValueError(f"Model '{llm_model}' not recognised. Please specify a supported model.")
