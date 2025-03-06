import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Διαβάζει τα δεδομένα και εξασφαλίζει σωστή κωδικοποίηση
def load_data(file_path):
    df = pd.read_csv(file_path, header=None, names=["M", "N", "D", "computed_makespan", "error", "time"], encoding="ISO-8859-1")
    return df

# Υπολογίζει τον μέσο όρο του error και του time για κάθε (M, N)
def compute_averages(df):
    return df.groupby(["M", "N"])[["error", "time"]].mean().reset_index()

# Συναρτήσεις για plotting

def plot_graph(x, y, hue, data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=x, y=y, hue=hue, data=data, marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title=hue)
    plt.grid(True)
    plt.savefig(filename)
    plt.show()

def save_to_excel(data_dict, output_file):
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# Διαδρομή του αρχείου
file_path = "results.txt"
data = load_data(file_path)
averaged_data = compute_averages(data)

# Δημιουργία και αποθήκευση γραφικών
plot_graph("N", "time", "M", averaged_data, "Χρόνος Εκτέλεσης vs N (ανά M)", "N", "Χρόνος (s)", "plot_time_vs_N.png")
plot_graph("N", "error", "M", averaged_data, "Σφάλμα vs N (ανά M)", "N", "Σφάλμα", "plot_error_vs_N.png")
plot_graph("M", "time", "N", averaged_data, "Χρόνος Εκτέλεσης vs M (ανά N)", "M", "Χρόνος (s)", "plot_time_vs_M.png")
plot_graph("M", "error", "N", averaged_data, "Σφάλμα vs M (ανά N)", "M", "Σφάλμα", "plot_error_vs_M.png")

time_avg_N = averaged_data.groupby("N")["time"].mean().reset_index()
plot_graph("N", "time", None, time_avg_N, "Μέσος Χρόνος Εκτέλεσης vs N", "N", "Μέσος Χρόνος (s)", "plot_avg_time_vs_N.png")

# Αποθήκευση δεδομένων σε Excel
data_dict = {
    "Time_vs_N_per_M": averaged_data.pivot(index="N", columns="M", values="time"),
    "Error_vs_N_per_M": averaged_data.pivot(index="N", columns="M", values="error"),
    "Time_vs_M_per_N": averaged_data.pivot(index="M", columns="N", values="time"),
    "Error_vs_M_per_N": averaged_data.pivot(index="M", columns="N", values="error"),
    "Avg_Time_vs_N": time_avg_N
}

save_to_excel(data_dict, "experiment_results.xlsx")
