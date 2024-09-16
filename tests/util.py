import json

from hubspot.cms.blogs.blog_posts.rest import RESTResponse
from urllib3 import HTTPResponse


def mkresponse(data, status=200, reason="OK"):
    body = json.dumps(data).encode("utf-8")
    return RESTResponse(HTTPResponse(body=body, status=status, reason=reason))
