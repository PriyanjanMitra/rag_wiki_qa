import os

from config import config

_lf = None


def get_langfuse():
    global _lf
    if _lf is None:
        sk = config.langfuse_secret_key or os.environ.get("LANGFUSE_SECRET_KEY")
        pk = config.langfuse_public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
        host = config.langfuse_host or os.environ.get("LANGFUSE_HOST", "http://langfuse:3000")
        if sk and pk:
            from langfuse import Langfuse
            _lf = Langfuse(secret_key=sk, public_key=pk, host=host)
    return _lf
