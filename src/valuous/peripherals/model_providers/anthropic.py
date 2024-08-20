from anthropic import Anthropic

from valuous.settings import settings

anthropic = Anthropic(api_key=settings.anthropic_api_key)
