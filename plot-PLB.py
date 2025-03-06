import pandas as pd
import matplotlib.pyplot as plt
import re

# Function to read and process data from a text file
def process_txt_file(file_path):
    with open(file_path, "r") as file:
        data = file.readlines()
    
    # Regular expression pattern to extract values
    pattern = r"T = (\d+),N = (\d+) , calibr = \d+, sec = ([\d.]+)"
    
    # Extract data using regex
    matches = [re.findall(pattern, line) for line in data]
    matches = [item for sublist in matches for item in sublist]  # Flatten list
    
    df = pd.DataFrame(matches, columns=["T", "N", "sec"])
    
    # Convert data types
    df = df.astype({"T": int, "N": int, "sec": float})
    
    return df

# Function to plot the processed data
def plot_data(df):
    # Compute the mean sec for each (T, N) pair
    df_mean = df.groupby(["T", "N"], as_index=False)["sec"].mean()
    
    # Pivot table for plotting
    df_pivot = df_mean.pivot(index="N", columns="T", values="sec")
    
    # Plot
    plt.figure(figsize=(8, 5))
    for T in df_pivot.columns:
        plt.plot(df_pivot.index, df_pivot[T], marker='o', label=f'T = {T}')
    
    plt.xlabel("N")
    plt.ylabel("Mean sec")
    plt.title("Mean sec for each T and N pair")
    plt.legend(title="T values")
    plt.grid(True)
    plt.show()

# Example usage
file_path = "outputLSBT.txt"  # Replace with your actual file path
df = process_txt_file(file_path)
plot_data(df)
