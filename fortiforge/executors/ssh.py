class SSHExecutor:
    """SSH executor stub using paramiko (not used by default). Enforces least privilege and explicit authorization."""
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def execute(self, host: dict, commands: list[str]):
        raise RuntimeError("SSHExecutor disabled in demo. Enable only with explicit authorization and consent.")
