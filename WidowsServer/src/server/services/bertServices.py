from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import torch
import torch.nn.functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model and tokenizer
model = DistilBertForSequenceClassification.from_pretrained("./fine_tuned_model")
model.to(device)
tokenizer = DistilBertTokenizer.from_pretrained("./fine_tuned_model")
tokenizer.to(device)

def tokenize_input(sentence : str):
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    return inputs

def bert_inference(inputs : dict):
    outputs = model(**inputs)
    predictions = outputs.logits
    return predictions

def post_process(predictions : list):
    probs = F.softmax(predictions, dim = -1)
    emotions = ['amazement', 'anger', 'cheekiness', 'disgust', 'fear', 'grief', 'joy', 'out of breath', 'pain', 'sadness', 'neutral']
    result = dict(zip(emotions, probs))
    idx = torch.argmax(predictions, dim = -1)
    maxProb = predictions[idx]
    return emotions, idx, maxProb, result