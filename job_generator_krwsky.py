import random

def edgecoloring(n):
    if n % 2 == 0: m = n-1
    else: m=n

    d = m // 2

    C = []

    for i in range(m):
        M = [((i+j) % m + 1, (i-j) % m + 1) for j in range(1,d+1)]
        if n % 2 == 0: M.append((i+1,n))
        C.append(M)
    return C


def split_number(n,k):
    if n == 0: return k*[0]
    L = list(range(1,n))
    S = random.sample(L,k-1)
    S.sort()
    S = [0]+S+[n]
    R = k*[0]
    for i in range(k):
        R[i] = S[i+1] - S[i]
    return R


def random_jobs(m, n, p, output_file = "tasks.txt"):

    if m % 2 == 1:
       print("Cannot create instance. Number of machines must be even")
       return

    if n < m*(m-1) == 0:
       print("Cannot create instance. Number of jobs must be at least" + str(m*(m-1)))
       return

    R = split_number(n-m*(m-1)//2,(m-1))
    N = [x + m // 2 for x in R] 
    D = [((x + 3) // 4)*p for x in N]

    C = edgecoloring(m)

    J = []
    for i in range(m-1):
        F = (m//2)*[1]
        for k in range(N[i]-m//2):
            r = random.randint(0,m//2-1)
            F[r] = F[r]+1
        for j in range(m//2):
            E = split_number(D[i],F[j])
            a = C[i][j][0]
            b = C[i][j][1]
            J = J + [(a,b,t) for t in E]

    random.shuffle(J)
    with open(output_file, 'w') as f:
        for j in J:
            f.write(str(j[0]) + " " + str(j[1]) + " " + str(j[2]) + "\n")
                    
    return sum(D)

random_jobs(m=6, n=1000, p=20, output_file = "inputs.txt")


