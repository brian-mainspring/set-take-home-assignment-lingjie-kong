class PowerManager:
    def __init__(self, capacity=1000.0):
        self.capacity = capacity
        self.remaining = capacity

    def consume(self, controller_name, amount):
        """
        Attempt to draw `amount` units of power from the battery.

        Return True if power was available and has been deducted.
        Return False if the battery cannot cover the request (no deduction made).
        """
        # TODO: Implement power consumption. Return True if power was available, False if not.
        pass

    def is_depleted(self):
        return self.remaining <= 0.0

    def remaining_pct(self):
        return max(0.0, (self.remaining / self.capacity) * 100.0)
