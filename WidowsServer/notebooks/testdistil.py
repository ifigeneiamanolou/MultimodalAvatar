# Before running the script create a python virtual environment and install the following 
# libraries:
# 1. datasets
# 2. torch
# 3. transformers
# 4. transformers[torch]

# Import libraries
from datasets import load_dataset, Dataset, DatasetDict
import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import classification_report
import numpy as np
import os

def train():
    # check gpu is available
    if torch.cuda.is_available():
        print("GPU is available")
    else:
        print("GPU is not available")
    print(torch.__version__)

    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

    # Import Go-Emotions
    emotions_db = load_dataset("mrm8488/goemotions")

    # Inspect dataset
    emotions_db.set_format(type="pandas")

    # Audio2Face emotions
    columns =  [
        'amazement', 'anger', 'cheekiness', 'disgust', 'fear', 'grief', 'joy', 'out of breath', 'pain', 'sadness', 'neutral'
    ]

    # Custom dataframe
    custom_df = pd.DataFrame(columns = columns)
    train_db = emotions_db['train'].to_pandas()

    # Emotion columns
    custom_df['amazement'] = train_db['amusement'] + train_db['realization'] + train_db['surprise'] + train_db['admiration']
    custom_df['anger'] = train_db['anger'] + train_db['annoyance'] + train_db['disapproval']
    custom_df['cheekiness'] = train_db['caring'] + train_db['love'] + train_db['desire']
    custom_df['disgust'] = train_db['disgust'] + train_db['remorse']
    custom_df['fear'] = train_db['fear'] + train_db['nervousness']
    custom_df['grief'] = train_db['grief']
    custom_df['joy'] = train_db['joy'] + train_db['pride'] + train_db['optimism'] + train_db['gratitude'] + train_db['relief'] + train_db['excitement']
    custom_df['out of breath'] = train_db['confusion']
    custom_df['pain'] = train_db['disappointment']
    custom_df['sadness'] = train_db['sadness'] + train_db['embarrassment']
    custom_df['neutral'] = train_db['neutral'] + train_db['approval'] + train_db['curiosity']

    # Text column
    custom_df['text'] = train_db['text']

    # Remove columns with all elements zero
    custom_df = custom_df[(custom_df.T != 0).any()]
    custom_dataset = Dataset.from_pandas(custom_df)

    # Load tokenizer
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

    # Pre processing
    def pre_process(examples):
        return tokenizer(examples['text'][0], truncation = True, padding = 'max_length')

    # Apply tokenization with batches
    distil_dataset = custom_dataset.map(pre_process, batch_size = 10)

    def add_label(example):
        example['label'] = [example[col] for col in columns]
        return example

    distil_dataset = distil_dataset.map(add_label)

    ds_train_devtest = distil_dataset.train_test_split(test_size=0.2, seed=42)
    ds_devtest = ds_train_devtest['test'].train_test_split(test_size=0.5, seed=42)

    ds_splits = DatasetDict({
        'train': ds_train_devtest['train'],
        'eval': ds_devtest['train'],
        'test': ds_devtest['test']
    })
    print(ds_splits)

    # Load DistilBERT model for classification
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=11)

    # Setting up training settings
    batch_size = 64
    training_args = TrainingArguments(
        output_dir="./results",          # Directory for saving results
        learning_rate=2e-5,              # Initial learning rate
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=2,              # Number of epochs
        weight_decay=0.01,               # Regularization
        logging_dir="./logs",            # Directory for logs
        logging_steps=10,                 # Log every 10 steps
    )

    trainer = Trainer(
        model = model,                             # The DistilBERT model
        args = training_args,                      # Training arguments
        train_dataset = ds_splits['train'],        # Training data
        eval_dataset= ds_splits['eval'],           # Validation data
    )

    # Start training
    trainer.train()

    # Evaluate general performance
    predictions = trainer.predict(ds_splits['test'])
    preds = np.argmax(predictions.predictions, axis = 1)
    actual_labels = ds_splits['test']['labels']
    print(classification_report(actual_labels, preds))

    # Error analysis
    for idx, (actual, pred) in enumerate(zip(actual_labels, preds)):
        print(f"Example {idx}: \n")
        print(f"Sentence: {ds_splits['test']['text'][idx]} \n")
        print(f"Actual: { actual} \n")
        print(f"Predicted {pred} \n")
        print("\n")
    
    # Save the model and tokenizer
    model.save_pretrained(os.path.join(BASE_DIR, "../../../data/fine_tuned_model"))
    tokenizer.save_pretrained(os.path.join(BASE_DIR, "../../../data/fine_tuned_model"))

if __name__ =="__main__":
    train()