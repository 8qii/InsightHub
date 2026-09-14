from app.errors import AppError


class KnowledgeProviderUnavailable(AppError):
    def __init__(self) -> None:
        super().__init__(
            503, "knowledge_provider_unavailable", "The knowledge provider is unavailable."
        )


class KnowledgeProviderTimeout(AppError):
    def __init__(self) -> None:
        super().__init__(504, "knowledge_provider_timeout", "The knowledge provider timed out.")


class KnowledgeAuthenticationError(AppError):
    def __init__(self) -> None:
        super().__init__(
            502,
            "knowledge_authentication_error",
            "The knowledge provider rejected authentication.",
        )


class KnowledgeWorkspaceNotFound(AppError):
    def __init__(self) -> None:
        super().__init__(
            404,
            "knowledge_workspace_not_found",
            "The requested knowledge workspace was not found.",
        )


class KnowledgeInvalidResponse(AppError):
    def __init__(self) -> None:
        super().__init__(
            502,
            "knowledge_invalid_response",
            "The knowledge provider returned an invalid response.",
        )


class KnowledgeQueryFailed(AppError):
    def __init__(self) -> None:
        super().__init__(
            502,
            "knowledge_query_failed",
            "The knowledge provider could not complete the query.",
        )
