class Dandere2xSuspendManagement:

    def __init__(self):
        self._suspended = False

    def is_suspended(self):
        return self._suspended

    def suspend(self):
        self._suspended = True

    def unsuspend(self):
        self._suspended = False
