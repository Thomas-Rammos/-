from collections import defaultdict
import random

def normalize_machine_names(machine_list):
    """
    Αφαιρεί κενά, βάζει πεζά, π.χ. ["M1","M2"] -> ["m1","m2"]
    """
    return [m.strip().lower() for m in machine_list if m.strip()]


def read_jobs_from_file(filename):
    """
    Διαβάζει εργασίες από το αρχείο:
       M1 M2 : 10
       m3 : 5
    κ.λπ.
    Επιστρέφει ένα λεξικό jobs, όπου το κλειδί είναι tuple μηχανών (π.χ. ('m1','m2')),
    και η τιμή λίστα από χρόνους [10,5,...].
    """
    total_time = 0
    jobs = defaultdict(list)
    with open(filename, 'r') as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split(":")
                if len(parts) != 2:
                    print(f"Παράλειψη γραμμής {line_num}: '{line}' (Μη έγκυρη μορφή)")
                    continue
                machines_part = parts[0].split()
                machines = tuple(sorted(normalize_machine_names(machines_part)))
                time_val = int(parts[1].strip())
                total_time += time_val
                jobs[machines].append(time_val)
            except ValueError as ve:
                print(f"Λανθασμένη τιμή στη γραμμή {line_num}: {line} (Σφάλμα: {ve})")
            except Exception as e:
                print(f"Απροσδόκητο σφάλμα στη γραμμή {line_num}: {e}")
    return jobs


def partition_jobs_goesman(jobs, machine):
    """
        Διαχωρίζει τα μονομηχανιακά jobs της μορφής (machine,) σε (Long) και (Short) σύμφωνα με βελτιωμένη λογική:
         - Αν έχω ένα job τότε το βάζω στο S_{iL}
         - Αν υπάρχει job >= 2/3 της συνολικής διάρκειας, το βάζουμε μόνο του στο S_{iL}.
         - Αν καμία εργασία δεν είναι >= 2/3, επιλέγουμε εργασίες για το S_{iL} έτσι ώστε:
           1/3 <= sum(S_{iL}) <= 2/3 της συνολικής διάρκειας.
         - Εξασφαλίζουμε ότι sum(S_{iL}) >= sum(S_{iS}).
        """
    # Συνολικός χρόνος μηχανής και προσωρινή αποθήκευση χρόνου κάθε εργασίας
    machine_total_time = 0
    timeslist = []
    for key, value in jobs.items():
        # Εξασφαλίζουμε ότι λαμβάνονται μόνο οι μονομηχανιακές εργασίες
        if key == (machine,):
            machine_total_time += sum(value)
            timeslist.extend(value)  # Προσθήκη όλων των χρόνων στη λίστα

    # Υπολογισμός ορίων
    threshold_13 = machine_total_time / 3.0
    threshold_23 = 2.0 * machine_total_time / 3.0

    # Αρχικοποίηση Long (S_L) και Short (S_S)
    S_L = []
    S_S = []

    # Αν έχω μόνο ένα στοιχείο
    if len(timeslist) == 1:
        S_L.append(timeslist[0])
        #print("S_L = ", sum(S_L))
        #print("S_S = ", sum(S_S))
        return S_L, S_S


    # Αν η μεγαλύτερη εργασία είναι >= 2/3 του συνολικού χρόνου
    max_val = max(timeslist)
    if max_val >= threshold_23 or len(timeslist) == 2:
        S_L.append(max_val)
        timeslist.remove(max_val)
        S_S = timeslist  # Οι υπόλοιπες εργασίες στο S_S
        #print("S_L = ", sum(S_L))
        #print("S_S = ", sum(S_S))
        return S_L, S_S


    # Γραμμικός καταμερισμός εργασιών για 1/3 <= sum(S_L) < 2/3
    running_sum = 0
    for tj in timeslist:
        if running_sum + tj < threshold_23:
            S_L.append(tj)
            running_sum += tj
            if running_sum >= threshold_13:
                break

    # Οι υπόλοιπες εργασίες πηγαίνουν στο S_S
    temp_timeslist = timeslist.copy()
    for x in S_L:
        temp_timeslist.remove(x)
    S_S = temp_timeslist


    # Εξασφάλιση συνθήκης: sum(S_L) >= sum(S_S) σε περίπτωση που η S_L έχει πάνω από ένα στοιχείο
    #if( (sum(S_L) > threshold_23) and len(S_L) == 1):
       # return S_L, S_S
    #else:
    while sum(S_L) < sum(S_S):
        # Μετακίνηση της μικρότερης εργασίας από το S_S στο S_L
        ind = random.randint(0,len(S_S) - 1)
        S_L.append(S_S[ind])
        S_S.remove(S_S[ind])

    #print("S_L = ", sum(S_L))
    #print("S_S = ", sum(S_S))
    return S_L, S_S

# Υπολογισμος μεταβλητων
def calculate_partition_values(jobs):
    """ Υπολογίζει και επιστρέφει τις βασικές τιμές L, S και p. """
    L1, S1 = partition_jobs_goesman(jobs, 'm1')
    L2, S2 = partition_jobs_goesman(jobs, 'm2')
    L3, S3 = partition_jobs_goesman(jobs, 'm3')

    values = {
        'L1': sum(L1), 'S1': sum(S1),
        'L2': sum(L2), 'S2': sum(S2),
        'L3': sum(L3), 'S3': sum(S3),
        'p1': sum(jobs.get(('m1',), [])),
        'p2': sum(jobs.get(('m2',), [])),
        'p3': sum(jobs.get(('m3',), [])),
        'p12': sum(jobs.get(('m1', 'm2'), [])),
        'p13': sum(jobs.get(('m1', 'm3'), [])),
        'p23': sum(jobs.get(('m2', 'm3'), [])),
    }
    return values

def calculatePathValue_AB(typegraph,A_val, B_val, C_val, D_val, E_val, F_val):
    # Ορισμός των paths μόνο για τον τύπο του γράφου
    if typegraph == "A":
        paths = [
            (A_val + C_val + E_val, "A->C->E"),
            (A_val + D_val + E_val, "A->D->E"),
            (A_val + D_val + F_val, "A->D->F"),
            (B_val + D_val + E_val, "B->D->E"),
            (B_val + D_val + F_val, "B->D->F"),
        ]
    elif typegraph == "B":
        paths = [
            (A_val + C_val + D_val + F_val, "A->C->D->F"),
            (A_val + E_val + F_val, "A->E->F"),
            (B_val + D_val + F_val, "B->D->F"),
        ]
    else:
        return 0, "No path"

    return paths

# Για τα Α και Β
def calculate_makespan_AB(typegraph, partition_values,inverted=False):
    # Επιλογή του συγκεκριμένου μονοπατιού μόνο
    if typegraph == 'A1':
        values = ("A",
            partition_values['p12'], partition_values['p3'],
            partition_values['p1'], partition_values['p23'],
            partition_values['p13'], partition_values['p2'],
        )
    elif typegraph == 'A2':
        values = ("A",
            partition_values['p12'], partition_values['p3'],
            partition_values['p2'], partition_values['p13'],
            partition_values['p23'], partition_values['p1'],
        )
    elif typegraph == 'A3':
        values = ("A",
            partition_values['p23'], partition_values['p1'],
            partition_values['p3'], partition_values['p12'],
            partition_values['p13'], partition_values['p2'],
        )
    elif typegraph == 'B1':
        values = ("B",
            partition_values['p12'], partition_values['p3'],
            partition_values['p1'], partition_values['p13'],
            partition_values['p2'], partition_values['p23'],
        )
    elif typegraph == 'B2':
        values = ("B",
            partition_values['p12'], partition_values['p3'],
            partition_values['p2'], partition_values['p23'],
            partition_values['p1'], partition_values['p13'],
        )
    elif typegraph == 'B3':
        values = ("B",
            partition_values['p23'], partition_values['p1'],
            partition_values['p3'], partition_values['p13'],
            partition_values['p2'], partition_values['p12'],
        )

    paths = calculatePathValue_AB(*values)
    # Επιστροφή του μέγιστου makespan και της καλύτερης διαδρομής
    max_val, best_path = max(paths, key=lambda x: x[0])

    return max_val, best_path


def calculatePathValue_CD(A_val, B_val, C_val, D_val, E_val, F_val, G_val):
    # DAG-based paths:
    # 1) A->D->F
    pathADF = A_val + D_val + F_val
    # 2) A->C->E->F
    pathACEF = A_val + C_val + E_val + F_val
    # 3) A->C->E->G
    pathACEG = A_val + C_val + E_val + G_val
    # 4) B->E->F
    pathBEF = B_val + E_val + F_val
    # 5) B->E->G
    pathBEG = B_val + E_val + G_val
    makespan_paths = [pathADF, pathACEF, pathACEG, pathBEF, pathBEG]
    return makespan_paths


# -----------------------------------
# Συνάρτηση υπολογισμού για Schedule C (C12, C13, C21, C23, C31, C32) και D αντίστοιχα
# -----------------------------------
def calculate_makespan_CD(schedule_type, partition_values, inverted=False):
    """ Υπολογίζει το makespan για το συγκεκριμένο schedule type (C ή D). """
    L_key = 'L' if not inverted else 'S'
    S_key = 'S' if not inverted else 'L'

    # Επιλογή του συγκεκριμένου μονοπατιού μόνο
    if schedule_type[1:] == '12':
        values = (
            partition_values['p12'], partition_values['p3'],
            partition_values[f'{L_key}1'], partition_values['p2'],
            partition_values['p13'], partition_values['p23'],
            partition_values[f'{S_key}1']
        )
    elif schedule_type[1:] == '13':
        values = (
            partition_values['p13'], partition_values['p2'],
            partition_values[f'{L_key}1'], partition_values['p3'],
            partition_values['p12'], partition_values['p23'],
            partition_values[f'{S_key}1']
        )
    elif schedule_type[1:] == '21':
        values = (
            partition_values['p12'], partition_values['p3'],
            partition_values[f'{L_key}2'], partition_values['p1'],
            partition_values['p23'], partition_values['p13'],
            partition_values[f'{S_key}2']
        )
    elif schedule_type[1:] == '23':
        values = (
            partition_values['p23'], partition_values['p1'],
            partition_values[f'{L_key}2'], partition_values['p3'],
            partition_values['p12'], partition_values['p13'],
            partition_values[f'{S_key}2']
        )
    elif schedule_type[1:] == '31':
        values = (
            partition_values['p13'], partition_values['p2'],
            partition_values[f'{L_key}3'], partition_values['p1'],
            partition_values['p23'], partition_values['p12'],
            partition_values[f'{S_key}3']
        )
    elif schedule_type[1:] == '32':
        values = (
            partition_values['p23'], partition_values['p1'],
            partition_values[f'{L_key}3'], partition_values['p2'],
            partition_values['p13'], partition_values['p12'],
            partition_values[f'{S_key}3']
        )
    else:
        return 0, "No path"

    # Υπολογισμός του makespan μόνο για το συγκεκριμένο μονοπάτι
    makespan_paths = calculatePathValue_CD(*values)
    max_val = max(makespan_paths)
    idx = makespan_paths.index(max_val)
    paths_descriptions = ["A->D->F", "A->C->E->F", "A->C->E->G", "B->E->F", "B->E->G"]

    return max_val, paths_descriptions[idx]

def find_best_strategy(strategy_group, calculate_fn, partition_values, inverted=False):
    best_strategy = None
    best_makespan = float('inf')

    for strat in strategy_group:
        ms, path = calculate_fn(strat, partition_values, inverted=inverted)
        print(f"{strat}: makespan={ms}, path={path}")
        if ms < best_makespan:
            best_makespan = ms
            best_strategy = strat

    return best_strategy, best_makespan


def main():
    filename = "tasks.txt"
    jobs = read_jobs_from_file(filename)
    if not jobs:
        print("Σφάλμα: Δεν βρέθηκαν έγκυρες εργασίες στο αρχείο.")
        return

    print("===== Εργασίες που φορτώθηκαν =====")
    for k, v in jobs.items():
        print(f"{k} -> {v}")
        print(sum(v))
    partition_values = calculate_partition_values(jobs)

    # Ορισμός στρατηγικών ανά ομάδα
    strategy_groups = {
        'A': ['A1', 'A2', 'A3'],
        'B': ['B1', 'B2', 'B3'],
        'C': ['C12', 'C13', 'C21', 'C23', 'C31', 'C32'],
        'D': ['D12', 'D13', 'D21', 'D23', 'D31', 'D32']
    }

    # Υπολογισμοί για κάθε ομάδα στρατηγικών
    results = {}

    for schedule, strategies in strategy_groups.items():
        print(f"\n===== Αποτελέσματα Schedule {schedule} =====")
        calculate_fn = calculate_makespan_CD if schedule in ['C', 'D'] else calculate_makespan_AB
        inverted = (schedule == 'D')

        best_strategy, best_makespan = find_best_strategy(strategies, calculate_fn, partition_values, inverted)
        print(f"Καλύτερη στρατηγική {schedule}: {best_strategy} με makespan={best_makespan}")
        results[schedule] = (best_makespan, best_strategy)

    # Εύρεση συνολικά καλύτερης στρατηγικής
    best_overall_makespan = min(value[0] for value in results.values())
    best_schedules = [
        (schedule, strategy[1])
        for schedule, strategy in results.items()
        if strategy[0] == best_overall_makespan
    ]

    print("\n===== Καλύτερες Στρατηγικές Συνολικά =====")
    for schedule, strategy in best_schedules:
        print(f"Schedule: {schedule} με στρατηγική {strategy} και makespan={best_overall_makespan}")

    print("\n===== ΤΕΛΟΣ ΥΠΟΛΟΓΙΣΜΩΝ =====")


if __name__ == "__main__":
    main()
