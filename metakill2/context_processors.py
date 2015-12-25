from .settings import VERSION


def version_provider(request):
    return {'metakill_version': VERSION}