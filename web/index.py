"""
Root level test.
"""

def app(request, context=None):
    """Test app."""
    return "Root test OK"


def handler(request, context=None):
    """Handler for Vercel."""
    return "Root test OK"
