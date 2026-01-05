import json
import logging
import os
import typing as t
from copy import deepcopy
from pathlib import Path

import hubspot
from click import confirm
from hubspot import HubSpot
from hubspot.cms.blogs.blog_posts import BlogPost
from hubspot.files import File

logger = logging.getLogger(__name__)


class HubSpotAdapter:
    """
    Wrapper around the HubSpot client, with additional
    functionality for blog posts and files.
    """

    # The options for all file operations.
    FILE_OPTIONS = {
        "access": "PUBLIC_INDEXABLE",
        "overwrite": False,
        "duplicateValidationStrategy": "NONE",
        "duplicateValidationScope": "EXACT_FOLDER",
    }

    def __init__(self, access_token: str):
        """
        Wrap HubSpot client instance.
        """
        if not access_token:
            raise ValueError("Communicating with the HubSpot API needs an access token")
        self.hs = HubSpot(access_token=access_token)

    def get_or_create_blogpost(self, article: "HubSpotBlogPost", autocreate: t.Optional[bool] = True) -> BlogPost:
        """
        When a blog post exists (either by name or resource identifier),
        return it. If it does not exist, create it.
        """
        if not article.name:
            raise ValueError("Blog post needs a 'name'")
        try:
            return self.get_blogpost_by_name(article.name)
        except FileNotFoundError as ex:
            msg = f"Blog post does not exist: {article.name}"
            logger.warning(msg)
            if not autocreate:
                raise hubspot.cms.blogs.blog_posts.exceptions.NotFoundException(msg) from ex
            if not article.content_group_id:
                raise ValueError("Blog (content group) identifier is required for creating a blog post") from ex
            logger.info(f"Creating: {article}")
            post = BlogPost(name=article.name, slug=article.name, content_group_id=article.content_group_id)
            return self.hs.cms.blogs.blog_posts.basic_api.create(post)

    def get_blogpost_by_name(self, name: str) -> BlogPost:
        """
        Find blog post by name.
        """
        response_types_map = {
            200: "CollectionResponseWithTotalBlogPostForwardPaging",
        }
        response = self.hs.cms.blogs.blog_posts.basic_api.api_client.call_api(
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

    def get_or_create_file(self, file: "HubSpotFile") -> File:
        """
        When a file exists, return its instance metadata.
        If it does not exist, upload/create it.

        https://developers.hubspot.com/docs/api/files/files
        https://legacydocs.hubspot.com/docs/methods/files/v3/upload_new_file
        """
        try:
            return self.get_file_by_name(file)
        except FileNotFoundError as ex:
            logger.warning(f"File does not exist: {file.name}")
            if file.folder_id and file.folder_path:
                raise ValueError("Use either `folder_id` or `folder_path`, but not both") from ex

            logger.info(f"Creating: {file}")

            if file.folder_id:
                return self.hs.files.files_api.upload(
                    file=file.source,
                    file_name=file.name,
                    folder_id=file.folder_id,
                    options=json.dumps(self.FILE_OPTIONS),
                )
            elif file.folder_path:  # noqa: RET505
                return self.hs.files.files_api.upload(
                    file=file.source,
                    file_name=file.name,
                    folder_path=file.folder_path,
                    options=json.dumps(self.FILE_OPTIONS),
                )

    def get_file_by_name(self, file: "HubSpotFile") -> File:
        """
        Find file by name.
        """
        if not file.name:
            raise ValueError("File name missing")
        if file.folder_id:
            file_stem = Path(file.name).stem
            logger.info(f"Searching for '{file_stem}' in folder id '{file.folder_id}'")
            response = self.hs.files.files_api.do_search(name=file_stem, parent_folder_ids=[file.folder_id])
        elif file.folder_path:
            logger.info(f"Searching for '{file.name}' in folder path '{file.folder_path}'")
            path = Path(file.folder_path) / file.name
            response = self.hs.files.files_api.do_search(path=str(path))
        else:
            raise ValueError("Folder is required when searching for files, please specify `folder_id` or `folder_path`")

        if not response.results:
            raise FileNotFoundError(f"File not found in folder. id={file.folder_id}, path={file.folder_path}")
        result: File = response.results[0]
        logger.info(f"Found file: id={result.id}, path={result.path}, url={result.url}")
        return result

    def save_file(self, file_id: str, source: str):
        """
        Save / overwrite existing file.
        """
        return self.hs.files.files_api.replace(file_id=file_id, file=source, options=json.dumps(self.FILE_OPTIONS))

    def delete_file_by_id(self, identifier: str) -> t.Optional[File]:
        """
        Delete file by file identifier.
        """
        response = self.hs.files.files_api.do_search(ids=[identifier])
        if not response.results:
            logger.info(f"File not found: id={identifier}")
            return None
        result: File = response.results[0]
        return self.do_delete_file_by_id(result.id)

    def delete_files_by_path(self, path: str) -> None:
        """
        Delete files by path.
        """
        response = self.hs.files.files_api.do_search(path=path)
        if not response.results:
            logger.info(f"Files not found: path={path}")
            return
        result: File
        for result in response.results:
            try:
                self.do_delete_file_by_id(result.id)
            except hubspot.files.exceptions.NotFoundException:
                pass

    def do_delete_file_by_id(self, identifier: str) -> File:
        """
        Effectively delete file by file identifier, confirming the delete action.
        """
        file = self.hs.files.files_api.get_by_id(identifier)
        logger.info(f"About to delete file: id='{file.id}'\n{file}")
        if os.environ.get("CONFIRM") == "yes":
            outcome = True
        else:
            outcome = confirm("Please confirm deletion (archival)")
        if outcome is True:
            return self.hs.files.files_api.archive(file.id)
        return None


class HubSpotBlogPost:
    """
    Wrap a HubSpot blog post.
    """

    def __init__(
        self,
        hubspot_adapter: HubSpotAdapter,
        identifier: t.Optional[str] = None,
        name: t.Optional[str] = None,
        content_group_id: t.Optional[str] = None,
        autocreate: t.Optional[bool] = True,
    ):
        self.hsa = hubspot_adapter
        self.hs = hubspot_adapter.hs
        self.post: t.Optional[BlogPost] = None
        self.content_group_id = content_group_id
        self.autocreate = autocreate

        if identifier and name:
            raise ValueError("Either 'identifier' or 'name' must be specified, not both")
        if not identifier and not name:
            raise ValueError("One of 'identifier' or 'name' must be specified")
        self.identifier = identifier
        self.name = name
        self.load()

    def __str__(self):
        return f"{self.__class__.__name__} identifier={self.identifier}, name={self.name}"

    def load(self):
        """
        Load blog post from HubSpot API, either by identifier, or by name.
        """
        logger.info(f"Loading blog post: {self}")
        if self.identifier:
            self.post = self.hs.cms.blogs.blog_posts.basic_api.get_by_id(self.identifier)
            self.name = self.post.name
        elif self.name:
            self.post = self.hsa.get_or_create_blogpost(self, autocreate=self.autocreate)
            self.identifier = self.post.id

    def save(self):
        """
        Save / overwrite existing blog post at HubSpot API.
        """
        logger.info(f"Saving blog post: {self}")
        post: BlogPost = deepcopy(self.post)
        post.created = None
        post.updated = None
        return self.hs.cms.blogs.blog_posts.basic_api.update(self.identifier, post)

    def delete(self):
        """
        Delete / archive blog post.
        """
        logger.info(f"Deleting blog post: {self.post}")

        if os.environ.get("CONFIRM") == "yes":
            outcome = True
        else:
            outcome = confirm("Please confirm deletion (archival)")
        if outcome is True:
            return self.hs.cms.blogs.blog_posts.basic_api.archive(self.identifier)
        return None


class HubSpotFile:
    """
    Wrap a HubSpot file.
    """

    def __init__(
        self,
        hubspot_adapter: HubSpotAdapter,
        source: t.Union[str, Path],
        identifier: t.Optional[str] = None,
        name: t.Optional[str] = None,
        folder_id: t.Optional[str] = None,
        folder_path: t.Optional[str] = None,
    ):
        self.hsa = hubspot_adapter
        self.hs = hubspot_adapter.hs
        self.source = source
        self.folder_id = folder_id
        self.folder_path = folder_path
        self.file: t.Optional[File] = None

        if identifier and name:
            raise ValueError("Either 'identifier' or 'name' must be specified, not both")
        if not identifier and not name:
            raise ValueError("One of 'identifier' or 'name' must be specified")

        if folder_id and folder_path:
            raise ValueError("One of 'folder_id' or 'folder_path' must be specified, not both")
        if not folder_id and not folder_path:
            raise ValueError(
                "Folder is required for uploading files, please specify either `folder_id` or `folder_path`"
            )

        self.identifier = identifier
        self.name = name
        self.load()

    def __str__(self):
        return (
            f"{self.__class__.__name__} identifier={self.identifier}, "
            f"name={self.name}, folder={self.folder_id or self.folder_path}"
        )

    def load(self):
        """
        Load file from HubSpot API, either by identifier, or by name.
        """
        logger.info(f"Loading file: {self}")
        if self.identifier:
            self.file = self.hs.files.files_api.get_by_id(self.identifier)
            self.name = self.file.name
        elif self.name:
            self.file = self.hsa.get_or_create_file(self)
            self.identifier = self.file.id

    def save(self):
        """
        Save / overwrite / replace existing file at HubSpot API.
        """
        if not self.identifier:
            raise ValueError(f"Unable to save file without identifier: {self}")
        if not self.source:
            raise ValueError(f"Unable to save file without source: {self}")
        logger.info(f"Saving file: {self}")
        return self.hsa.save_file(file_id=self.identifier, source=str(self.source))

    def delete(self):
        """
        Delete / archive file.
        """
        logger.info(f"Deleting file: {self}")
        self.hs.files.files_api.archive(self.identifier)
