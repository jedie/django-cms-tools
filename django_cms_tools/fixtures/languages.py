
import warnings


try:
    from django_tools.fixture_tools.languages import iter_languages # for compatibility
except ImportError as err:
    raise ImportError("%s (It's new in django-tools v0.39.2")


warnings.warn("django_cms_tools.fixtures.languages will be removed in the future! Use from django-tools!", PendingDeprecationWarning)
