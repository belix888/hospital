"""
Simple test endpoint to verify routing works.
"""

def app(request, context=None):
    """Simple test app."""
    return "Test OK"


def handler(request, context=None):
    """Handler for Vercel."""
    return "Test OK"
