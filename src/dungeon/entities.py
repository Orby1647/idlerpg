

class Entity:
    def __init__(self, x, y, hp, atk, df):
        self.x, self.y = x, y
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.df = df

    def is_alive(self):
        return self.hp > 0

class Player(Entity):
    def __init__(self, x, y, max_hp, atk, df, regen):
        super().__init__(x, y, max_hp, atk, df)
        self.max_hp = max_hp
        self.hp = max_hp
        self.regen = regen
        self.gold = 0
        self.kills = 0

    def tick_regen(self):
        if self.regen > 0 and self.hp < self.max_hp:
            self._frac = getattr(self, "_frac", 0.0)
            self._frac += self.regen
            while self._frac >= 1.0:
                self.hp = min(self.max_hp, self.hp + 1)
                self._frac -= 1.0

class Monster(Entity):
    pass
