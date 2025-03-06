import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import re
from collections import defaultdict

def parse_line(line):
    """Extracts values from each line."""
    pattern = re.compile(r'ratio=(\d+\.\d+), N=(\d+), A=(\d+)\((A\d+)\), B=(\d+)\((B\d+)\), C=(\d+)\((C\d+)\), D=(\d+)\((D\d+)\), bestMakespan=(\d+)\((\w+)\), OPT=(\d+\.\d+), error=(\d+\.\d+), time=(\d+\.\d+)')
    match = pattern.search(line)
    if match:
        return {
            "ratio": float(match.group(1)),
            "N": int(match.group(2)),
            "A": int(match.group(3)),
            "B": int(match.group(5)),
            "C": int(match.group(7)),
            "D": int(match.group(9)),
            "bestMakespan": int(match.group(11)),
            "scheduler": match.group(12),
            "OPT": float(match.group(13)),
            "error": float(match.group(14)),
            "time": float(match.group(15))
        }
    return None
def load_data(filename):
    """Loads data from the file and structures it."""
    data = []
    with open(filename, 'r') as file:
        for line in file:
            parsed = parse_line(line)
            if parsed:
                data.append(parsed)

    df = pd.DataFrame(data)

    # Μετατροπή του time σε float
    if "time" in df.columns:
        df["time"] = pd.to_numeric(df["time"], errors="coerce")  # Μετατροπή σε float, αγνοώντας μη αριθμητικά δεδομένα

    # Διατήρηση μόνο αριθμητικών στηλών
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df = df[numeric_columns]

    # Αφαίρεση σειρών που έχουν NaN (λόγω πιθανής αποτυχίας μετατροπής σε αριθμούς)
    df = df.dropna()

    # Ομαδοποίηση και υπολογισμός μέσου όρου
    df = df.groupby(["ratio", "N"], as_index=False).mean()

    return df


# Load data
file_path = "all_results.txt"
df = load_data(file_path)
# 8. Μέσος όρος time ανεξαρτήτως ratio για κάθε N
avg_time_per_N = df.groupby("N")["time"].mean()
plt.figure(figsize=(10, 6))
plt.plot(avg_time_per_N.index, avg_time_per_N.values, marker='o', linestyle='-', color='red')
plt.xlabel("N")
plt.ylabel("Mean Time (ms)")
plt.title("Μέσος Όρος του Time για κάθε N (Ανεξαρτήτως Ratio)")
plt.grid()
plt.show()
# 1. Boxplot του time για κάθε ratio
plt.figure(figsize=(10, 6))
sns.boxplot(x=df["ratio"], y=df["time"])
plt.xlabel("Ratio")
plt.ylabel("Time")
plt.title("Boxplot του Time για κάθε Ratio")
plt.grid()
plt.show()

# 2. Scatter plot: Time vs N
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df["N"], y=df["time"], hue=df["ratio"], palette="coolwarm")
plt.xlabel("N")
plt.ylabel("Time")
plt.title("Scatter Plot: Time σε σχέση με N για διαφορετικά Ratios")
plt.legend(title="Ratio")
plt.grid()
plt.show()

# 3. Heatmap του time με άξονες N και ratio
df_pivot = df.pivot(index="N", columns="ratio", values="time")
plt.figure(figsize=(12, 8))
sns.heatmap(df_pivot, cmap="coolwarm", annot=True, fmt=".3f", linewidths=0.5)
plt.xlabel("Ratio")
plt.ylabel("N")
plt.title("Heatmap του Time ανά N και Ratio")
plt.show()

# 4. Histogram του time
plt.figure(figsize=(10, 6))
sns.histplot(df["time"], bins=20, kde=True)
plt.xlabel("Time")
plt.ylabel("Frequency")
plt.title("Κατανομή του Time")
plt.grid()
plt.show()

# 5. Μέσος όρος time ανά ratio
avg_time_per_ratio = df.groupby("ratio")["time"].mean()
plt.figure(figsize=(10, 6))
avg_time_per_ratio.plot(kind="bar", color="skyblue")
plt.xlabel("Ratio")
plt.ylabel("Mean Time")
plt.title("Μέσος Όρος του Time για κάθε Ratio")
plt.grid(axis="y")
plt.show()

# 6. Τα καλύτερα Schedules με βάση το χαμηλότερο Time
best_schedules = df.loc[df.groupby("ratio")["time"].idxmin()]
plt.figure(figsize=(10, 6))
sns.barplot(x=best_schedules["ratio"], y=best_schedules["time"], hue=best_schedules["N"], dodge=True)
plt.xlabel("Ratio")
plt.ylabel("Lowest Time")
plt.title("Τα καλύτερα Schedules με βάση το χαμηλότερο Time")
plt.legend(title="N")
plt.grid()
plt.show()

# 7. Time vs N για κάθε Ratio
plt.figure(figsize=(10, 6))
for ratio in df["ratio"].unique():
    subset = df[df["ratio"] == ratio]
    plt.plot(subset["N"], subset["time"], marker='o', label=f'ratio={ratio}')
plt.xlabel("N")
plt.ylabel("Time")
plt.title("Time vs N για κάθε Ratio")
plt.legend(title="Ratio")
plt.grid()
plt.show()

# 8. Scheduler Performance Analysis (A, B, C, D) based on time
schedulers = ["A", "B", "C", "D"]
for scheduler in schedulers:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df["N"], y=df[scheduler], hue=df["ratio"], palette="coolwarm")
    plt.xlabel("N")
    plt.ylabel(f"{scheduler} Scheduler Value")
    plt.title(f"{scheduler} Scheduler Performance across N and Ratio (Time)")
    plt.legend(title="Ratio")
    plt.grid()
    plt.show()

# 9. Boxplot των schedulers για να συγκρίνουμε τα A, B, C, D σε time
plt.figure(figsize=(10, 6))
df_melted = df.melt(id_vars=["ratio", "N"], value_vars=["A", "B", "C", "D"], var_name="Scheduler", value_name="Value")
sns.boxplot(x=df_melted["Scheduler"], y=df_melted["Value"])
plt.xlabel("Scheduler")
plt.ylabel("Time")
plt.title("Σύγκριση των Schedulers (A, B, C, D) ως προς το Time")
plt.grid()
plt.show()
