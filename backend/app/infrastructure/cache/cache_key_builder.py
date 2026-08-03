import hashlib
import json


class CacheKeyBuilder:
    """
    Deterministic cache key generation.

    Builds stable, collision-resistant keys from a namespace
    and a set of key/value segments, so that the same inputs
    always produce the same key.
    """

    @staticmethod
    def build(
        namespace: str,
        *segments,
        **fields,
    ) -> str:

        parts = [namespace]

        parts.extend(str(segment) for segment in segments)

        for key in sorted(fields):

            value = fields[key]

            if isinstance(value, (dict, list)):
                value = json.dumps(
                    value,
                    sort_keys=True,
                    default=str,
                )

            parts.append(f"{key}={value}")

        raw = "|".join(parts)

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def prompt_key(
        prompt_name: str,
        prompt_text: str,
        version: str | None = None,
    ) -> str:

        return CacheKeyBuilder.build(
            "prompt",
            prompt_name,
            version or "active",
            text=prompt_text,
        )

    @staticmethod
    def ai_response_key(
        model: str,
        prompt: str,
    ) -> str:

        return CacheKeyBuilder.build(
            "ai",
            model,
            text=prompt,
        )

    @staticmethod
    def semantic_key(
        embedding_hash: str,
        threshold_bucket: float = 0.0,
    ) -> str:

        return CacheKeyBuilder.build(
            "semantic",
            embedding_hash,
            bucket=threshold_bucket,
        )
