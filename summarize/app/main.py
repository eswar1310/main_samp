from fastapi import FastAPI, UploadFile, File
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')

app = FastAPI()

def preprocess_text(text):
    text = text.lower()
    text = ''.join([char for char in text if char.isalnum() or char.isspace()])
    return text

def tokenize_text(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    return sentences, words

def remove_stopwords(words):
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words

def chunk_text(text, max_length):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in sentences:
        sentence_length = len(word_tokenize(sentence))
        if current_length + sentence_length > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def summarize_text(text):
    model_name = "philschmid/bart-large-cnn-samsum"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    summarizer = pipeline('summarization', model=model, tokenizer=tokenizer)
    
    max_input_length = 1024  
    chunks = chunk_text(text, max_input_length)
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, do_sample=False, truncation=True)
        summaries.append(summary[0]['summary_text'])
    
    return ' '.join(summaries)

def identify_primary_speaker(conversation):
    speaker_pattern = re.compile(r"Speaker (\d+):")
    speakers = speaker_pattern.findall(conversation)
    speaker_counts = Counter(speakers)
    primary_speaker = speaker_counts.most_common(1)[0][0]
    return primary_speaker

def extract_primary_speaker_dialogue(conversation, primary_speaker):
    primary_dialogue = []
    lines = conversation.split("\n")
    speaker_pattern = re.compile(rf"Speaker {primary_speaker}:\s*(.*)")
    
    for line in lines:
        match = speaker_pattern.match(line)
        if match:
            primary_dialogue.append(line)  
    
    return "\n".join(primary_dialogue)

@app.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    content = await file.read()
    raw_text = content.decode('utf-8')
    
    preprocessed_text = preprocess_text(raw_text)
    sentences, words = tokenize_text(preprocessed_text)
    filtered_words = remove_stopwords(words)
    summary = summarize_text(raw_text)
    
    primary_speaker = identify_primary_speaker(raw_text)
    primary_speaker_dialogue = extract_primary_speaker_dialogue(raw_text, primary_speaker)
    primary_speaker_summary = summarize_text(primary_speaker_dialogue)
    
    return {
        "summary": summary,
        "primary_speaker": f"Speaker {primary_speaker}",
        "primary_speaker_summary": primary_speaker_summary
    }
