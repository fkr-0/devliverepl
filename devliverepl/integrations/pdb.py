"""Standard library pdb integration."""

import sys
from devliverepl.capture import get_current_context


def attach(frame=None):
    """Attach pdb debugger with captured context.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.

    Example:
        >>> from devliverepl.integrations import attach_pdb
        >>> attach_pdb()  # Drops into pdb with captured context
    """
    import pdb

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        # Use caller's frame
        frame = sys._getframe(1)

    pdb.Pdb().set_trace(frame)


__all__ = ["attach"]
