import math


class Job:
    """
    Κάθε Job έχει: id, d, p
      - id: αναγνωριστικό
      - d : deadline
      - p : υπόλοιπος χρόνος εκτέλεσης
    """
    def __init__(self, job_id, d, p):
        self.id = job_id
        self.d = d
        self.p = p


def edf_schedule(jobs, start, end):
    """
    EDF Scheduling σε [start, end) με πραγματικό preemption.
    Επιστρέφει:
       - job_execs: λεξικό {job_id: [(start1, end1), (start2, end2), ...]}
    και στο ίδιο διάστημα μειώνει inline το p για κάθε job.
    """
    job_execs = {job.id: [] for job in jobs}
    t = start

    while t < end:
        feasible = [j for j in jobs if j.p > 0]
        if not feasible:
            t += 1  # Αν δεν υπάρχει διαθέσιμη εργασία, προχωράμε
            continue

        # EDF sort (πρώτα οι δουλειές με τη μικρότερη προθεσμία)
        feasible.sort(key=lambda j: j.d)
        chosen = feasible[0]

        steps = min(chosen.p, end - t)
        job_execs[chosen.id].append((t, t + steps))

        chosen.p -= steps  # Μειώνουμε το υπόλοιπο p
        t += steps  # Προχωράμε χρονικά

    return job_execs


def plb_scheduling(jobs, T):
    """
    Preemptive Lazy Binning scheduling με βελτιώσεις για μεγάλα T.
    Επιστρέφει:
     - calibrations (list)
     - exec_intervals: {job_id: [(start,end), ...]} συνολικά σε όλα τα intervals
    """
    jobs.sort(key=lambda j: j.d)  # Ταξινόμηση κατά προθεσμία
    calibrations = []
    exec_intervals = {jb.id: [] for jb in jobs}

    while len(jobs) > 0:
        t = max(j.d for j in jobs)
        sum_all = sum(j.p for j in jobs)
        k_index = 0

        for i in range(len(jobs) - 1, -1, -1):
            job_i = jobs[i]
            limit_time = job_i.d - sum_all
            if t > limit_time:
                t = limit_time
                k_index = i
            if t < 0:
                print("Infeasible schedule: start time < 0")
                return [], {}
            sum_all -= job_i.p

        d_k = jobs[k_index].d
        delta = d_k - t
        if delta < 0:
            print("Infeasible schedule: d_k < t.")
            return [], {}

        max_deadline = max(j.d for j in jobs)
        adaptive_T = min(T, max_deadline - t)  # Περιορισμός του T
        needed_segments = max(1, math.ceil(delta / adaptive_T))
        u = min(t + needed_segments * adaptive_T, max_deadline)

        calibrations.append(u)  # Προσθήκη μόνο του τελικού calibration

        # --- [t, d_k): EDF για jobs[:k_index+1]
        left_jobs = jobs[:k_index + 1]
        left_execs = edf_schedule(left_jobs, t, d_k)
        for jb_id, intervals in left_execs.items():
            exec_intervals[jb_id].extend(intervals)

        jobs = [j for j in jobs if j.p > 0]  # Αφαίρεση ολοκληρωμένων εργασιών

        # --- [d_k, u): EDF για τα υπόλοιπα
        if d_k < u:
            right_jobs = [jj for jj in jobs if jj.p > 0]
            right_execs = edf_schedule(right_jobs, d_k, u)
            for jb_id, intervals in right_execs.items():
                exec_intervals[jb_id].extend(intervals)
            jobs = [j for j in jobs if j.p > 0]

    return calibrations, exec_intervals


def main(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]

    T = int(lines[0])
    N = int(lines[1])

    all_jobs = []
    idx_line = 2
    for _ in range(N):
        parts = lines[idx_line].split()
        idx_line += 1
        job_id = int(parts[0])
        d = int(parts[2])
        p = int(parts[3])
        all_jobs.append(Job(job_id, d, p))

    calibrations, exec_intervals = plb_scheduling(all_jobs, T)

    print("\n--- FINAL SCHEDULING OUTPUT ---")
    print("Calibration times:", calibrations)

    sorted_ids = sorted(exec_intervals.keys())
    for j_id in sorted_ids:
        intervals = exec_intervals[j_id]
        if not intervals:
            continue
        intervals.sort(key=lambda x: x[0])
        print(f"Job {j_id} executed in intervals:")
        for (st, en) in intervals:
            print(f"   [{st}, {en}) => duration {en - st}")


if __name__ == "__main__":
    main("input_LSB.txt")
