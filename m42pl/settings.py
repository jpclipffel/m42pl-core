class Settings:
    def get(self, scope: str, name: str, default = None):
        return default


SETTINGS = Settings()
