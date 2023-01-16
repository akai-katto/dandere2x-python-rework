class Dandere2xGuiIsRunning:

    def __init__(self):
        self._is_running = True

    def kill(self):
        self._is_running = False

    def status(self):
        return self._is_running
