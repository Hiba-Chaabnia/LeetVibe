"""Import shim for the Mistral SDK.

mistralai 2.x moved the client to `mistralai.client`; 1.x exposes it at the
top level. The call surface LeetVibe uses is identical across both.
"""

from __future__ import annotations

try:
    from mistralai.client import Mistral
except ImportError:  # mistralai < 2
    from mistralai import Mistral

__all__ = ["Mistral"]
