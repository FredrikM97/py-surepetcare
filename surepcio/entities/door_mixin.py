class door_mixin:
   def is_curfew_active(self):
        curfews = self.control.curfew if isinstance(self.control.curfew, list) else ([self.control.curfew] if self.control.curfew else [])
        now = datetime.now().time()
        return any(
            c.enabled and (
            (c.lock_time <= c.unlock_time and c.lock_time <= now <= c.unlock_time) or
            (c.lock_time > c.unlock_time and (now >= c.lock_time or now <= c.unlock_time))
           ) for c in curfews)
