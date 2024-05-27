from tqdm import tqdm

# Create a lock for synchronizing access to tqdm
lock = tqdm.get_lock()


class ProgressBar(tqdm):
    def __init__(self, max_val: int, start_message: str = None):
        super().__init__(total=max_val, desc=start_message,
                         leave=False,
                         bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]')

    def update(self, n=1):
        """Increment the progress bar position"""
        with lock:
            super().update(n)
