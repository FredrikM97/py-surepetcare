import hashlib
import logging

from aiohttp import ClientResponse

logger = logging.getLogger(__name__)


class CacheHeaders:
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
        logger.debug("Populated headers for resource %s: %s", resource_id, self.resources[resource_id])

    def headers(self, endpoint):
        """Return the headers of the response."""
        resource_id = self.endpoint_to_resource_id(endpoint)
        if resource_id in self.resources:
            return self.resources[resource_id]
        return {}

    def eTag(self, response, resource_id):
        """Return the ETag header."""
        etag = response.get("Etag")
        # if etag:
        #    etag = etag.strip('"')
        if etag != self.resources[resource_id].get("If-None-Match", None):
            self.resources[resource_id]["If-None-Match"] = etag

    def endpoint_to_resource_id(self, endpoint):
        logger.debug("Converting endpoint %s to resource ID", endpoint)
        if "/api" in endpoint:
            resource_id = endpoint.split("/api", 1)[1]
        else:
            resource_id = endpoint

        resource_id = hashlib.sha1(resource_id.encode()).hexdigest()
        return resource_id
