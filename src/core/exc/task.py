class TaskCancelled(RuntimeError):
    def __init__(self):
        super().__init__("Task was cancelled by user")
