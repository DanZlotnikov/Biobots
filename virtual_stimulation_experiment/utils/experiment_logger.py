import os
import time
import statistics
from datetime import datetime


class ExperimentLogger:
    class ReactionTracker:
        def __init__(self):
            self.current_stim_time = None
            self.first_reaction_time = None
            self.latencies = []

        def on_stimulation(self, t):
            self.current_stim_time = t
            self.first_reaction_time = None

        def on_reaction(self, t):
            # Only record latency for FIRST reaction after stimulus
            if (
                self.current_stim_time is not None
                and self.first_reaction_time is None
            ):
                self.first_reaction_time = t
                self.latencies.append(t - self.current_stim_time)

        def stats(self):
            if not self.latencies:
                return None, None, 0

            mean = sum(self.latencies) / len(self.latencies)
            median = statistics.median(self.latencies)
            return mean, median, len(self.latencies)

    # --------------------------------------------------
    # Logger init
    # --------------------------------------------------

    def __init__(self, base_dir="logs"):
        os.makedirs(base_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(base_dir, f"experiment_{ts}.log")

        self.total_movements = 0
        self.total_stimulations = 0
        self.total_reactions = 0

        self.reactions = self.ReactionTracker()

        self._write_header()

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _now(self):
        return time.time()

    def _fmt(self, t):
        return f"{t:.3f}"

    def _write(self, msg):
        with open(self.log_path, "a") as f:
            f.write(msg + "\n")

    def _write_header(self):
        self._write("=" * 60)
        self._write("EXPERIMENT START")
        self._write(f"Start time: {datetime.now().isoformat()}")
        self._write("=" * 60)

    # --------------------------------------------------
    # Public logging API
    # --------------------------------------------------

    def log_trial_start(self):
        t = self._now()
        self._write(f"[{self._fmt(t)}] TRIAL_START")

    def log_movement(self):
        t = self._now()
        self.total_movements += 1
        self._write(f"[{self._fmt(t)}] MOVEMENT")

    def log_stimulation(self, stim_type="visual+audio"):
        t = self._now()
        self.total_stimulations += 1
        self.reactions.on_stimulation(t)
        self._write(f"[{self._fmt(t)}] STIMULATION type={stim_type}")

    def log_reaction(self):
        t = self._now()
        self.total_reactions += 1
        self.reactions.on_reaction(t)
        self._write(f"[{self._fmt(t)}] REACTION_MOVEMENT")

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    def close(self):
        non_reaction_movements = self.total_movements - self.total_reactions
        mean_rt, median_rt, n_rt = self.reactions.stats()

        self._write("=" * 60)
        self._write("EXPERIMENT END")
        self._write(f"End time: {datetime.now().isoformat()}")
        self._write("-" * 60)
        self._write(f"Total movements: {self.total_movements}")
        self._write(f"Total stimulations: {self.total_stimulations}")
        self._write(f"Total reactions to stimulation: {self.total_reactions}")
        self._write(f"Total movements NOT reactions: {non_reaction_movements}")

        self._write("-" * 60)
        self._write("REACTION TIME STATISTICS")

        if n_rt == 0:
            self._write("No reaction times recorded.")
        else:
            self._write(f"Reaction count: {n_rt}")
            self._write(f"Mean reaction time: {mean_rt:.3f} s")
            self._write(f"Median reaction time: {median_rt:.3f} s")

        self._write("=" * 60)
