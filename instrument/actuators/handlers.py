class InvalidPortException(Exception):
    def __init__(self, value = 'Port not valid'):
        self.value = value
    def __str__(self):
        return repr(self.value)
