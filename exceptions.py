class ScrapeError(Exception):
    pass


class ScrapeTimeoutError(ScrapeError):
    pass


class NetworkError(ScrapeError):
    pass


class ContentNotFoundError(ScrapeError):
    pass


class UpstreamServerError(ScrapeError):
    pass


# llm errors
class LlmApiError(Exception):
    pass
