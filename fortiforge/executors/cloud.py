class CloudExecutor:
    """Cloud API executor stub (AWS/Azure).
    Requires user-provided credentials and explicit account authorization. Disabled by default.
    """
    def execute(self, actions):
        raise RuntimeError("CloudExecutor disabled in demo. Set explicit authorization to enable.")
