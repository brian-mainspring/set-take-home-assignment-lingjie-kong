class VanillaOrchid:
    TEMP_MIN = 21
    TEMP_MAX = 26

    def __init__(self):
        self.alive = True

    def daily_check(self, temperature):
        if temperature < self.TEMP_MIN or temperature > self.TEMP_MAX:
            self.alive = False

    def kill(self):
        self.alive = False
