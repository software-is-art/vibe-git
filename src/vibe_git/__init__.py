"""vibe-git: Friction-free git workflows for vibe coding."""

__version__ = "0.1.0"

# Beartype integration:
# We've explored using beartype_this_package() and beartype_package() for
# automatic type checking, but both have issues with FastMCP's @mcp.tool()
# decorator, which returns non-callable FunctionTool objects.
#
# The issue: When @mcp.tool() decorates a function, it replaces the function
# with a FunctionTool object. Beartype tries to decorate this object and fails
# because it's not callable.
#
# For now, we rely on manual @beartype decoration for individual functions,
# which gives us fine-grained control and avoids decorator conflicts.
# Most of our functions already have explicit type checking in place.
