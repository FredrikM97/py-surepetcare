import hashlib
import logging

from aiohttp import ClientResponse

logger = logging.getLogger(__name__)


class CacheHeaders:
    """Manages caching headers for API requests.
    Stored the apt/* endpoint as hashed keys with eTag.
    To determine if request already provided up-to-date data.
    """

    resources: dict[str, dict] = {}

    def __init__(self):
        self._headers = {}

    def clear_resources(self):
        self.resources = {}

    def populate_headers(self, response: ClientResponse):
        """Set the headers of the response."""
        resource_id = self.endpoint_to_resource_id(response.url.path)
        if resource_id not in self.resources:
            self.resources[resource_id] = {}

        self.eTag(response.headers, resource_id)

    def headers(self, endpoint):
        """Return the headers of the response."""
        resource_id = self.endpoint_to_resource_id(endpoint)
        if resource_id in self.resources:
            return self.resources[resource_id]
        return {}

    def eTag(self, response, resource_id):
        """Return the ETag header. Which is unique per resource."""
        etag = response.get("Etag")

        if etag != self.resources[resource_id].get("If-None-Match", None):
            logger.debug("Reading ETag header %s. New generated for resource_id %s", etag, resource_id)
            self.resources[resource_id]["If-None-Match"] = etag
        logger.debug("Reading ETag header %s. Using existing ETag for resource_id %s", etag, resource_id)

    def endpoint_to_resource_id(self, endpoint):
        """Convert an endpoint to a resource ID by hashing the endpoint path."""
        if "/api" in endpoint:
            resource_id = endpoint.split("/api", 1)[1]
        else:
            resource_id = endpoint

        resource_id = hashlib.sha1(resource_id.encode()).hexdigest()
        return resource_id
