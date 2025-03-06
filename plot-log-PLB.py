import re
import numpy as np
import matplotlib.pyplot as plt
from math import ceil

def read_and_process_file(filename):
    data_dict = {}
    
    with open(filename, 'r') as file:
        lines = file.readlines()[2:]  # Skip first two lines
    
    pattern = r"T = (\d+),N = (\d+) , calibr = \d+, sec = ([\d.]+)"
    
    for line in lines:
        match = re.search(pattern, line)
        if match:
            T, N, sec = int(match.group(1)), int(match.group(2)), float(match.group(3))
            key = (T, N)
            if key not in data_dict:
                data_dict[key] = []
            data_dict[key].append(sec)
    
    # Compute average sec for each (T, N) pair
    aggregated_data = {N: np.mean(times) for (T, N), times in data_dict.items()}
    
    return aggregated_data

def predict_intermediate_values(aggregated_data):
    min_N = min(aggregated_data.keys())
    max_N = max(aggregated_data.keys())
    
    predicted_data = {}
    
    for N in range(min_N, max_N + 1):
        if N in aggregated_data:
            predicted_data[N] = aggregated_data[N]
        else:
            T = ceil(np.sqrt(N))
            predicted_data[N] = (N ** 2) * (aggregated_data[max_N] / (max_N ** 2))  # Quadratic complexity assumption
    
    return predicted_data

def plot_data(aggregated_data):
    sorted_N = sorted(aggregated_data.keys())
    sorted_sec = [aggregated_data[N] for N in sorted_N]
    
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_N, sorted_sec, marker='o', label="T related with N square")
    plt.xlabel("N values")
    plt.ylabel("Average sec")
    plt.title("PLB Algorithm Performance with Prediction")
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    filename = "outputLSBlog.txt"  # Change this to your actual filename
    aggregated_data = read_and_process_file(filename)
    predicted_data = predict_intermediate_values(aggregated_data)
    plot_data(predicted_data)
