import os
import random
import math
def generate_random_input(N, T, p_min, p_max, file_path, d_ratio,K):
    """
    Γεννήτρια τυχαίων εργασιών για το PLB scheduler.
    """
    d_min = 2 * p_max      
    d_max = round(N * (p_min + p_max) / 2 * d_ratio)
    file = open(file_path, 'w', encoding='utf-8')
    
    for i in range(K):
        jobs_data = []
        for i in range(1, N + 1):
            d = random.randint(d_min, d_max)
            p = random.randint(p_min, p_max)
            r = 0
            jobs_data.append((i, r, d, p))
            
        file.write(f"{T}\n")
        file.write(f"{N}\n")
        for job_id, r, d, p in jobs_data:
            file.write(f"{job_id} {r} {d} {p}\n")
        file.write(f"\n")    
    print(f"[INFO] Created file: {file_path}")


def create_simulation_files(d_ratio_list, N_list, K, base_dir="simulationsLog2", p_min=1, p_max=100):
    """
    Δημιουργεί φακέλους και αρχεία με βάση τις λίστες d_ratio, T, και N.
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    for d_ratio in d_ratio_list:
        folder_name = f"simD_ratio{d_ratio}"
        folder_path = os.path.join(base_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        for N in N_list:
            T = math.ceil(math.log(N,2))
            file_name = f"simT{T}N{N}.txt"
            file_path = os.path.join(folder_path, file_name)
            generate_random_input(N, T, p_min, p_max, file_path, d_ratio,K)

    print("[INFO] Simulation files creation completed.")


if __name__ == "__main__":
    K = 15
    d_ratio_list = [1.5]
    N_list = [ 25000,36000, 40000,42000, 46000,50000,52000,56000, 60000]
    
    create_simulation_files(d_ratio_list, N_list, K)
