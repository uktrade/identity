import json
import logging

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

register = template.Library()


def load_manifest() -> dict:
    with settings.VITE_MANIFEST_PATH.open() as f:
        manifest = json.load(f)

    logger.debug("Vite manifest loaded")

    return manifest


manifest = load_manifest()


@register.simple_tag(takes_context=True)
def vite_css(context, filename: str) -> str:
    if settings.VITE_DEV:
        return ""

    return mark_safe(
        f'<link rel="stylesheet" href="{static(manifest[filename]["file"])}">'
    )


@register.simple_tag(takes_context=True)
def vite_js(context, filename: str) -> str:
    if settings.VITE_DEV:
        return ""

    return mark_safe(
        f'<script type="module" src="{static(manifest[filename]["file"])}"></script>'
    )


@register.simple_tag(takes_context=True)
def vite_local(context, filename: str) -> str:
    if not settings.VITE_DEV:
        return ""

    scripts = [
        f'<script type="module" src="{settings.VITE_DEV_SERVER_URL}/@vite/client"></script>',
        f'<script type="module" src="{settings.VITE_DEV_SERVER_URL}/{filename}"></script>',
    ]

    return mark_safe("\n".join(scripts))
