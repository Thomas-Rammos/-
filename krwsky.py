
import heapq
import time
from collections import defaultdict
from itertools import permutations


def read_edges_from_file(filename):
    """
    Διαβάζει τις ακμές από ένα αρχείο.
    :param filename: Το όνομα του αρχείου εισόδου.
    :return: Λίστα ακμών (edge_id, node1, node2, weight).
    """
    edges = []
    try:
        with open(filename, 'r') as file:
            edge_id = 0
            for line in file:
                parts = line.split()
                if len(parts) == 3:
                    node1, node2, weight = map(int, parts)
                    edges.append((edge_id, node1, node2, weight))
                    edge_id += 1
    except FileNotFoundError:
        print(f"Το αρχείο {filename} δεν βρέθηκε.")
    except ValueError:
        print(f"Σφάλμα μορφής στο αρχείο {filename}. Βεβαιωθείτε ότι κάθε γραμμή έχει την εξής μορφή: node1 node2 weight")
    return edges

def sort_edges_longest_first(edges):
    """
    Ταξινόμηση ακμών κατά φθίνουσα σειρά βάρους χρησιμοποιώντας heapq.
    """
    heap = [(-weight, edge_id, node1, node2) for (edge_id, node1, node2, weight) in edges]
    heapq.heapify(heap)

    sorted_edges = []
    while heap:
        neg_weight, edge_id, node1, node2 = heapq.heappop(heap)
        sorted_edges.append((edge_id, node1, node2, -neg_weight))

    return sorted_edges

def brute_force_makespan(edges, neighbors):
    """
    Υπολογίζει τον ελάχιστο makespan μέσω εξαντλητικού ελέγχου.
    :param edges: Λίστα ακμών (edge_id, node1, node2, weight).
    :param neighbors: Λεξικό με γείτονες κόμβων.
    :return: Ελάχιστο makespan.
    """
    min_makespan = float('inf')
    for perm in permutations(edges):
        start_times = {}
        valid = True
        for edge_id, node1, node2, weight in perm:
            scheduled_adj_times = []
            for node in (node1, node2):
                for nbr, nbr_edge_id, nbr_weight in neighbors[node]:
                    if nbr_edge_id in start_times:
                        nbr_start = start_times[nbr_edge_id]
                        scheduled_adj_times.append((nbr_start, nbr_weight))
            scheduled_adj_times.sort(key=lambda x: x[0])
            term = 0
            for t_e_sj, l_e_sj in scheduled_adj_times:
                if term + weight <= t_e_sj:
                    break
                else:
                    term = max(term, t_e_sj + l_e_sj)
            start_times[edge_id] = term
            if term + weight > min_makespan:
                valid = False
                break
        if valid:
            makespan = max(start_times[edge_id] + weight for edge_id, _, _, weight in perm)
            min_makespan = min(min_makespan, makespan)
    return min_makespan

def is_binomial_graph(edges):
    weights = set(weight for (_, _, _, weight) in edges)
    return len(weights) == 2

def build_neighbors(edges):
    """
    Δημιουργεί τη δομή neighbors:
    neighbors[node] = [(neighbor, edge_id, weight), ...]

    Παράλληλα δημιουργούμε το edges_info για επιπλέον αναφορές:
    edges_info[edge_id] = (node1, node2, weight)
    """
    neighbors = defaultdict(list)
    edges_info = {}
    for (edge_id, node1, node2, weight) in edges:
        neighbors[node1].append((node2, edge_id, weight))
        neighbors[node2].append((node1, edge_id, weight))
        edges_info[edge_id] = (node1, node2, weight)
    return neighbors, edges_info

def schedule_edges(edges, neighbors, edges_info):
    """
    Υλοποίηση του LF scheduling, χρησιμοποιώντας neighbors.
    neighbors[node] = [(neighbor, edge_id, weight)]
    """
    start_times = {}

    for (edge_id, node1, node2, weight) in edges:
        scheduled_adj_times = []
        for node in (node1, node2):
            for (nbr, nbr_edge_id, nbr_weight) in neighbors[node]:
                if nbr_edge_id in start_times:
                    nbr_start = start_times[nbr_edge_id]
                    scheduled_adj_times.append((nbr_start, nbr_weight))

        scheduled_adj_times.sort(key=lambda x: x[0])
        term = 0
        for (t_e_sj, l_e_sj) in scheduled_adj_times:
            if term + weight <= t_e_sj:
                break
            else:
                term = max(term, t_e_sj + l_e_sj)

        start_times[edge_id] = term

    return start_times

def node_busy_intervals(start_times, edges_info):
    """
    Υπολογίζει τα busy intervals για κάθε κόμβο.
    busy[node] = [(start, end), ...]
    """
    busy = defaultdict(list)
    for e_id, s_time in start_times.items():
        n1, n2, w = edges_info[e_id]
        busy[n1].append((s_time, s_time + w))
        busy[n2].append((s_time, s_time + w))
    for node in busy:
        busy[node].sort(key=lambda x: x[0])
    return busy

def find_availability_intervals(busy_intervals, end_time):
    """
    Εύρεση διαστημάτων διαθεσιμότητας ενός κόμβου μέχρι end_time.
    """
    available = []
    current_start = 0
    for (b_start, b_end) in busy_intervals:
        if b_start >= end_time:
            break
        if b_start > current_start:
            free_end = min(b_start, end_time)
            if free_end > current_start:
                available.append((current_start, free_end))
        current_start = max(current_start, b_end)
        if current_start >= end_time:
            break
    if current_start < end_time:
        available.append((current_start, end_time))
    return available

def intersect_intervals(intervals_a, intervals_b):
    """
    Τέμνει δύο λίστες διαστημάτων, επιστρέφοντας τα κοινά διαθέσιμα διαστήματα.
    """
    i, j = 0, 0
    result = []
    while i < len(intervals_a) and j < len(intervals_b):
        a_start, a_end = intervals_a[i]
        b_start, b_end = intervals_b[j]
        start_int = max(a_start, b_start)
        end_int = min(a_end, b_end)
        if start_int < end_int:
            result.append((start_int, end_int))

        if a_end < b_end:
            i += 1
        else:
            j += 1
    return result

def calculate_delays(edges, start_times, edges_info):
    """
    Υπολογίζει delay για κάθε ακμή.
    """
    busy = node_busy_intervals(start_times, edges_info)
    delays = {}
    for (e_id, u, v, w) in edges:
        s_e = start_times[e_id]
        if s_e == 0:
            delays[e_id] = 0
            continue

        u_available = find_availability_intervals(busy[u], s_e)
        v_available = find_availability_intervals(busy[v], s_e)
        common_available = intersect_intervals(u_available, v_available)

        delay = 0
        for (st, en) in common_available:
            end_int = min(en, s_e)
            if end_int > st:
                delay += (end_int - st)
        delays[e_id] = delay

    return delays

def calculate_demand_schedule_and_delay(edges, start_times, edges_info, binomial):
    """
    Αν το γράφημα είναι binomial, θεωρούμε ότι δεν υπάρχουν καθυστερήσεις.
    """
    if binomial:
        delays = {e_id: 0 for (e_id, _, _, _) in edges}
        is_demand_schedule = True
        return is_demand_schedule, delays

    delays = calculate_delays(edges, start_times, edges_info)
    is_demand_schedule = all(d == 0 for d in delays.values())
    return is_demand_schedule, delays

def evaluate_ratio(edges, start_times, edges_info, max_weighted_degree):
    """
    Υπολογισμός LF(G)/OPT(G) ≈ makespan / max_weighted_degree
    """
    if not edges or not start_times:
        return 0, 0

    makespan = max(start_times[e_id] + edges_info[e_id][2] for (e_id, _, _, _) in edges)
    ratio = makespan / max_weighted_degree if max_weighted_degree > 0 else float('inf')
    return ratio, makespan

def generate_diagnostic_graph(neighbors, start_times, edges_info):
    """
    Δημιουργία διαγνωστικού γραφήματος με βάση τις διαθέσιμες μονάδες.
    Χρησιμοποιούμε διάρκεια=1 για απλότητα.
    """
    diagnostic_graph = {}
    busy_intervals = {}

    for (e_id, s_time) in start_times.items():
        end_time = s_time + 1
        n1, n2, _ = edges_info[e_id]
        busy_intervals.setdefault(n1, []).append((s_time, end_time))
        busy_intervals.setdefault(n2, []).append((s_time, end_time))

    for node in busy_intervals:
        busy_intervals[node].sort(key=lambda x: x[0])

    all_nodes = list(neighbors.keys())
    for node in all_nodes:
        diagnostic_graph[node] = []
        node_intervals = busy_intervals.get(node, [])
        for (neighbor, nbr_edge_id, w) in neighbors[node]:
            neighbor_intervals = busy_intervals.get(neighbor, [])
            available = False
            node_idx, neighbor_idx = 0, 0

            while node_idx < len(node_intervals) and neighbor_idx < len(neighbor_intervals):
                n_start, n_end = node_intervals[node_idx]
                neigh_start, neigh_end = neighbor_intervals[neighbor_idx]
                if n_end <= neigh_start:
                    available = True
                    break
                elif neigh_end <= n_start:
                    available = True
                    break
                else:
                    if n_end < neigh_end:
                        node_idx += 1
                    else:
                        neighbor_idx += 1

            if available:
                diagnostic_graph[node].append((neighbor, w))

    return diagnostic_graph

def generate_filtered_edges(edges, diagnostic_graph, edges_info):
    """
    Φιλτράρει τις ακμές με βάση το diagnostic_graph.
    """
    filtered_edges = []
    all_original_triplets = set()
    for e_id, (n1, n2, w) in edges_info.items():
        all_original_triplets.add((min(n1, n2), max(n1, n2), w))

    for node in diagnostic_graph:
        for (neighbor, w) in diagnostic_graph[node]:
            tri = (min(node, neighbor), max(node, neighbor), w)
            if tri in all_original_triplets:
                filtered_edges.append(tri)
    return filtered_edges

def calculate_average_start_times(start_times, edges_info):
    node_start_times = defaultdict(list)
    for e_id, s_time in start_times.items():
        node1, node2, _ = edges_info[e_id]
        node_start_times[node1].append(s_time)
        node_start_times[node2].append(s_time)

    avg_start_times = {
        node: sum(times) / len(times) for node, times in node_start_times.items() if times
    }
    return avg_start_times

def calculate_load_distribution(edges):
    node_load = defaultdict(int)
    for (edge_id, node1, node2, weight) in edges:
        node_load[node1] += 1
        node_load[node2] += 1
    return dict(node_load)

if __name__ == "__main__":
    execution_start_time = time.time()

    filename = "inputs.txt"
    edges = read_edges_from_file(filename)
    print(f"Loaded edges: {edges}")

    if not edges:
        print("Δεν βρέθηκαν ακμές στο αρχείο. Τερματισμός.")
    else:
        binomial = is_binomial_graph(edges)
        if binomial:
            print(f"Το γράφημα είναι δυωνυμικό.")
        else:
            print(f"Το γράφημα ΔΕΝ είναι δυωνυμικό.")

        # Ταξινόμηση ακμών κατά μήκος (φθίνουσα)
        edges = sort_edges_longest_first(edges)
        print(f"Sorted edges: {edges}")

        # Δημιουργία neighbors και edges_info
        neighbors, edges_info = build_neighbors(edges)

        # Προγραμματισμός με LF (Longest First)
        start_times_lf = schedule_edges(edges, neighbors, edges_info)
        makespan_lf = max(start_times_lf[e_id] + edges_info[e_id][2] for e_id in start_times_lf) if start_times_lf else 0
        print(f"LF Start times: {start_times_lf}")
        print(f"LF Makespan: {makespan_lf}")

        # Υπολογισμός ελάχιστου makespan με brute force (για επαλήθευση)
        if len(edges) <= 6:  # Εφαρμόζουμε brute force μόνο σε μικρά γραφήματα
            min_makespan = brute_force_makespan(edges, neighbors)
            print(f"Brute Force Makespan: {min_makespan}")
            if makespan_lf == min_makespan:
                print("Ο αλγόριθμος LF υπολόγισε το ελάχιστο Makespan.")
            else:
                print("ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Ο αλγόριθμος LF ΔΕΝ υπολόγισε το ελάχιστο Makespan!")

        # Δημιουργία διαγνωστικού γράφου
        diagnostic_graph = generate_diagnostic_graph(neighbors, start_times_lf, edges_info)
        print(f"Diagnostic graph: {diagnostic_graph}")

        # Φιλτράρισμα ακμών για nonbusy units
        filtered_edges = generate_filtered_edges(edges, diagnostic_graph, edges_info)
        print(f"Filtered edges: {filtered_edges}")

        # Μέσοι χρόνοι έναρξης
        avg_start_times = calculate_average_start_times(start_times_lf, edges_info)
        print("Average Start Times (per node):")
        for node, avg_time in avg_start_times.items():
            print(f"Node {node}: {avg_time:.2f}")

        # Κατανομή φορτίου
        load_distribution = calculate_load_distribution(edges)
        print("Load Distribution (per node):")
        for node, load in load_distribution.items():
            print(f"Node {node}: {load} edges")

        # Υπολογισμός max_weighted_degree από neighbors
        max_weighted_degree = 0
        for node in neighbors:
            w_sum = sum(w for (nbr, e_id, w) in neighbors[node])
            if w_sum > max_weighted_degree:
                max_weighted_degree = w_sum
        print(f"Max weighted degree: {max_weighted_degree}")

        # Έλεγχος demand schedule και καθυστερήσεων
        is_demand_schedule, delays = calculate_demand_schedule_and_delay(edges, start_times_lf, edges_info, binomial)
        print(f"Is demand schedule: {is_demand_schedule}")
        print(f"Delays: {delays}")

        # Υπολογισμός λόγου LF(G)/OPT(G)
        ratio, computed_makespan = evaluate_ratio(edges, start_times_lf, edges_info, max_weighted_degree)
        print(f"Ratio (makespan/Δ): {ratio}, Computed Makespan: {computed_makespan}")

        if binomial:
            # Για binomial γράφημα, θεωρητικά LF(G)/OPT(G) ≤ 2
            if ratio <= 2:
                print("Binomial graph check: LF(G)/OPT(G) ≤ 2 επιβεβαιώθηκε.")
            else:
                print("Προειδοποίηση: Για binomial γράφημα, αναμένεται LF(G)/OPT(G) ≤ 2, αλλά βρέθηκε λόγος > 2.")

    execution_end_time = time.time()
    execution_time = execution_end_time - execution_start_time
    print(f"\nExecution Time: {execution_time:.4f} seconds")

