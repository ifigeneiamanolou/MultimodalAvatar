import pandas as pd
import os
from funasr import AutoModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

emotions = []

def emotion2vec():
    # Load the model
    model_id = "iic/emotion2vec_plus_large"
    print("loading model ... \n")

    model = AutoModel(
        model=model_id,
        hub="hf",  # "ms" or "modelscope" for China mainland users; "hf" or "huggingface" for other overseas users
    )

    print("loaded model \n")

    # Load dataset (stored optimally in parquet for faster loading)
    df = pd.read_parquet(os.path.join(BASE_DIR, "../../data/testing/savee.parquet"))
    print(df.head())

    # Filter by each emotion and select five audios from each
    emotions = df['emotion'].unique()
    for emotion in emotions:
        print(emotion)
        dfEmotion = df[df['emotion'] == emotion]
        head = dfEmotion.head()
        print(head)

        # Peform emotion recognition on each audio using emotion2vec 
        emotions = pd.Series()
        for _, row in head.iterrows():      # row is a Series
            emotionDetected = model.generate(row['audio'], language = "en")
            print(emotionDetected)
            emotions.add(emotionDetected)

        # Compare the predicted emotion with the actual for each emotion
        correct = head['emotion'] == emotions
        stats = pd.DataFrame([emotions, head['emotion'], correct])

        # Store descriptive statistics in a CSV file 
        stats.to_csv(path_or_buf = f"{emotion}.csv")

emotion2vec()