import random
import os


def split_number(n, k):
    if n == 0 or k <= 0:
        return [0] * k
    k = min(k, n)
    L = list(range(1, n))
    if len(L) < k - 1:
        S = L
    else:
        S = random.sample(L, k - 1)
    S.sort()
    S = [0] + S + [n]
    R = [S[i+1] - S[i] for i in range(k)]
    return R


def random_jobs(n, ratio, p):

    if n<8:
       print("Cannot create instance. Number of jobs is very small")
       return
    
    
    m2 = round(ratio / (3-ratio) * n)
    if m2 < 3 and ratio != 0:
        m2 = 3
    m1 = n - m2
    if m1 < 5:
        m1 = 5
        m2 = n - 5

    OPT = round((m2 + (m1 - m2) / 3) * p)
    
    D = round(OPT*ratio)  
    if D < 3 and ratio != 0:    
        D = 3
            
    R = split_number(D,3)

    D12 = R[0]    
    D13 = R[1]    
    D23 = R[2]

    E = OPT - D
    if E < 2 and ratio != 1:
        E = 2
        D = OPT - 2
        
        
    R = split_number(E,2)

    Ea = R[0]    
    Eb = R[1]    

    D1 = E + D23
    D2a = Ea
    D2b = Eb + D13
    D3a = Ea + D12
    D3b = Eb

    if D > 0:
        n12 = round(m2 * D12/D)
        n13 = round(m2 * D13/D) 
        n23 = m2 - n12 - n13
    else:
        n12 = 0
        n13 = 0 
        n23 = 0

    n2a = round(D2a/p) 
    n2b = round(D2b/p) 
    n3a = round(D3a/p) 
    n3b = round(D3b/p)
    n1 = m1 - n2a - n2b - n3a - n3b


    if D12 > 0:
        while n12 < 0:
            n12 =n12+1
            if n13 > n23: n13 = n13 - 1
            else: n23 = n23 - 1

    if D13 > 0 and n13 == 0:
        n13 = 1
        if n12 > n23: n12 = n12 - 1
        else: n23 = n23 - 1

    if D23 > 0 and n23 <= 0:
        n23 = 1
        if n12 > n13: n12 = n12 - 1
        else: n13 = n13 - 1



    while n1 <= 0:
        n1 = n1 + 1
        mx = max(n2a,n2b,n3a,n3b)
        if mx == n2a: n2a = n2a - 1
        elif mx == n2b: n2b = n2b - 1
        elif mx == n3a: n3a = n3a - 1
        else: n3b = n3b -1

    if n2a == 0:
        n2a = 1
        mx = max(n1,n2b,n3a,n3b)
        if mx == n1: n1 = n1 -1
        elif mx == n2b: n2b = n2b - 1
        elif mx == n3a: n3a = n3a - 1
        else: n3b = n3b - 1

    if n2b == 0:
        n2b = 1
        mx = max(n2a,n1,n3a,n3b) 
        if mx == n2a: n2a = n2a - 1
        elif mx == n1: n1 = n1 - 1
        elif mx == n3a: n3a = n3a - 1
        else: n3b = n3b - 1


    if n3a == 0:
        n3a = 1
        mx = max(n2a,n2b,n1,n3b)
        if mx == n2a: n2a = n2a - 1
        elif mx == n2b: n2b = n2b - 1
        elif mx == n1: n1 = n1 - 1
        else: n3b = n3b - 1


    if n3b == 0:
        n3b = 1
        mx = max(n2a,n2b,n3a,n1)
        if mx == n2a: n2a = n2a - 1
        elif mx == n2b: n2b = n2b - 1
        elif mx == n3a: n3a = n3a - 1
        else: n1 = n1 - 1


    J1 = split_number(D1,n1)
    J2 = split_number(D2a,n2a) + split_number(D2b,n2b)
    J3 = split_number(D3a,n3a) + split_number(D3b,n3b)
    J12 = split_number(D12,n12)
    J13 = split_number(D13,n13)
    J23 = split_number(D23,n23)

    Jobs = [("M1",j) for j in J1] + [("M2",j) for j in J2] + [("M3",j) for j in J3] + [("M1 M2",j) for j in J12] + [("M1 M3",j) for j in J13]  + [("M2 M3",j) for j in J23]
    random.shuffle(Jobs)
  
    return OPT, Jobs

def main():
    # Παράμετροι
    N_list = [100,1000,10000,20000,40000,60000,100000,150000,300000,600000,900000]  # Παράδειγμα τιμών N
    R_list = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]  # Παράδειγμα τιμών R
    K_rep = 12  # Αριθμός πειραμάτων

    # Δημιουργία φακέλου simulations
    base_dir = "simulations"
    os.makedirs(base_dir, exist_ok=True)

    for n in N_list:
        sim_folder = os.path.join(base_dir, f"px_simsN{n}")
        os.makedirs(sim_folder, exist_ok=True)
        
        for ratio in R_list:
            file_name = f"simN{n}R{ratio}.txt"
            file_path = os.path.join(sim_folder, file_name)
            
            with open(file_path, 'w') as f:
                for i in range(K_rep):
                    OPT,jobs = random_jobs(n=n,ratio=ratio, p=20)
                    f.write(f"{OPT}\n") 
                    if jobs:
                        for job in jobs:
                            f.write(f"{job[0]} : {job[1]}\n")
                        f.write("\n")  # Κενή γραμμή μεταξύ πειραμάτων

main()

