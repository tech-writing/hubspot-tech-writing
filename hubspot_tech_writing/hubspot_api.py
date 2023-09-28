import logging
import typing as t
from copy import deepcopy

from hubspot import HubSpot
from hubspot.cms.blogs.blog_posts import BlogPost

logger = logging.getLogger(__name__)


class HubSpotAdapter:
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("Communicating with the HubSpot API needs an access token")
        self.hs = HubSpot(access_token=access_token)

    def get_or_create_blogpost(self, article: "BlogArticle") -> BlogPost:
        try:
            return self.get_blogpost_by_name(article.name)
        except FileNotFoundError as ex:
            logger.warning(f"Blog post does not exist: {article.name}")
            if not article.content_group_id:
                raise ValueError("Blog (content group) identifier is required for creating a blog post") from ex
            logger.info(f"Creating: {article}")
            post = BlogPost(name=article.name, slug=article.name, content_group_id=article.content_group_id)
            return self.hs.cms.blogs.blog_posts.blog_post_api.create(post)

    def get_blogpost_by_name(self, name: str) -> BlogPost:
        response_types_map = {
            200: "CollectionResponseWithTotalBlogPostForwardPaging",
        }
        response = self.hs.cms.blogs.blog_posts.blog_post_api.api_client.call_api(
            "/cms/v3/blogs/posts",
            "GET",
            auth_settings=["oauth2"],
            response_types_map=response_types_map,
            query_params={"name": name},
            _return_http_data_only=True,
        )
        if not response.results:
            raise FileNotFoundError(f"Blog post not found: {name}")
        return response.results[0]


class BlogArticle:
    def __init__(
        self,
        hubspot_adapter: HubSpotAdapter,
        identifier: t.Optional[str] = None,
        name: t.Optional[str] = None,
        content_group_id: t.Optional[str] = None,
    ):
        self.hsa = hubspot_adapter
        self.hs = hubspot_adapter.hs
        self.post: t.Optional[BlogPost] = None
        self.content_group_id = content_group_id

        if identifier and name:
            raise ValueError("Either 'identifier' or 'name' must be specified, not both")
        if not identifier and not name:
            raise ValueError("One of 'identifier' or 'name' must be specified")
        self.identifier = identifier
        self.name = str(name)
        self.load()

    def __str__(self):
        return f"BlogArticle identifier={self.identifier}, name={self.name}"

    def load(self):
        logger.info(f"Loading: {self}")
        if self.identifier:
            self.post = self.hs.cms.blogs.blog_posts.blog_post_api.get_by_id(self.identifier)
            self.name = self.post.name
        elif self.name:
            self.post = self.hsa.get_or_create_blogpost(self)
            self.identifier = self.post.id

    def save(self):
        logger.info(f"Saving: {self}")
        post: BlogPost = deepcopy(self.post)
        post.created = None
        post.updated = None
        return self.hs.cms.blogs.blog_posts.blog_post_api.update(self.identifier, post)

    def delete(self):
        logger.info(f"Deleting: {self}")
        self.hs.cms.blogs.blog_posts.blog_post_api.archive(self.identifier)
