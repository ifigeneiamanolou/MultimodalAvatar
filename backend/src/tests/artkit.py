# Tests for measuring time required to generate artkit coefficients for variable length strings
from faker import Faker
import pandas as pd
from apis.main import generateAnimations
from time import perf_counter
import os

fake = Faker()
NUM_TESTS = 100
df = pd.DataFrame(columns = ['text', 'length', 'time'])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

async def run_test():
    global df
    for num in range(NUM_TESTS):
        print(f"Finished task {num}")
        
        # Generate fake string
        text = fake.text()

        # Measure its length
        length = len(text)

        start = perf_counter()
        # Generate coefficients
        await generateAnimations(text = text)

        # Store the total processing time
        end = perf_counter()
        processing_time = end - start

        # Store the result in a dataframe
        df.loc[num] = [text, length, processing_time]

    # Save raw test data
    path = os.path.join(BASE_DIR, "../../data/testing/processingTimes.csv")
    df.to_csv(path)

    # Generate summary statistics
    series = df["time"]
    summary = series.describe()

    # Save processed test data
    pathSummary = os.path.join(BASE_DIR, "../../data/testing/artkitStatistics.csv")
    summary.to_csv(pathSummary)

if __name__ == "__main__":
    async def perform():
        await run_test()