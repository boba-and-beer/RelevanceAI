from typing import List
from relevanceai.base import _Base


class DocumentsClient(_Base):
    def __init__(self, project, api_key):
        self.project = project
        self.api_key = api_key
        super().__init__(project, api_key)

    def list(
        self,
        dataset_id: str,
        select_fields=[],
        cursor: str = None,
        page_size: int = 20,
        include_vector: bool = True,
        random_state: int = 0,
    ):
        """
        Retrieve documents from a specified dataset. Cursor is provided to retrieve even more documents. Loop through it to retrieve all documents in the dataset.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        select_fields : list
            Fields to include in the search results, empty array/list means all fields.
        page_size: int
            Size of each page of results
        cursor: string
            Cursor to paginate the document retrieval
        include_vector: bool
            Include vectors in the search results
        random_state: int
            Random Seed for retrieving random documents.
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/list",
            method="GET",
            parameters={
                "select_fields": select_fields,
                "cursor": cursor,
                "page_size": page_size,
                "include_vector": include_vector,
                "random_state": random_state,
            },
        )

    def get(self, dataset_id: str, id: str, include_vector: bool = True):

        """
        Retrieve a document by its ID ("_id" field). This will retrieve the document faster than a filter applied on the "_id" field.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        id : string
            ID of a document in a dataset.
        include_vector: bool
            Include vectors in the search results
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/get",
            parameters={
                "id": id,
                "include_vector": include_vector,
            },
        )

    def bulk_get(
        self,
        dataset_id: str,
        ids: str,
        include_vector: bool = True,
        select_fields: list = [],
    ):

        """
        Retrieve a document by its ID ("_id" field). This will retrieve the document faster than a filter applied on the "_id" field. \n
        For single id lookup version of this request use datasets.documents.get.

        Parameters
        ----------
        dataset_id: string
            Unique name of dataset
        ids: list
            IDs of documents in the dataset.
        include_vector: bool
            Include vectors in the search results
        select_fields: list
            Fields to include in the search results, empty array/list means all fields.
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/bulk_get",
            parameters={
                "id": ids,
                "include_vector": include_vector,
                "select_fields": select_fields,
            },
        )

    def get_where(
        self,
        dataset_id: str,
        filters: list = [],
        cursor: str = None,
        page_size: int = 20,
        sort: list = [],
        select_fields: list = [],
        include_vector: bool = True,
        random_state: int = 0,
        is_random: bool = False,
    ):

        """
        Retrieve documents with filters. Cursor is provided to retrieve even more documents. Loop through it to retrieve all documents in the database. Filter is used to retrieve documents that match the conditions set in a filter query. This is used in advance search to filter the documents that are searched. \n

        The filters query is a json body that follows the schema of:

        >>> [
        >>>    {'field' : <field to filter>, 'filter_type' : <type of filter>, "condition":"==", "condition_value":"america"},
        >>>    {'field' : <field to filter>, 'filter_type' : <type of filter>, "condition":">=", "condition_value":90},
        >>> ]

        These are the available filter_type types: ["contains", "category", "categories", "exists", "date", "numeric", "ids"] \n

        "contains": for filtering documents that contains a string

        >>> {'field' : 'item_brand', 'filter_type' : 'contains', "condition":"==", "condition_value": "samsu"}

        "exact_match"/"category": for filtering documents that matches a string or list of strings exactly.

        >>> {'field' : 'item_brand', 'filter_type' : 'category', "condition":"==", "condition_value": "sumsung"}

        "categories": for filtering documents that contains any of a category from a list of categories.

        >>> {'field' : 'item_category_tags', 'filter_type' : 'categories', "condition":"==", "condition_value": ["tv", "smart", "bluetooth_compatible"]}

        "exists": for filtering documents that contains a field.

        >>> {'field' : 'purchased', 'filter_type' : 'exists', "condition":"==", "condition_value":" "}

        If you are looking to filter for documents where a field doesn't exist, run this:

        >>> {'field' : 'purchased', 'filter_type' : 'exists', "condition":"!=", "condition_value":" "}

        "date": for filtering date by date range.

        >>> {'field' : 'insert_date_', 'filter_type' : 'date', "condition":">=", "condition_value":"2020-01-01"}

        "numeric": for filtering by numeric range.

        >>> {'field' : 'price', 'filter_type' : 'numeric', "condition":">=", "condition_value":90}

        "ids": for filtering by document ids.

        >>> {'field' : 'ids', 'filter_type' : 'ids', "condition":"==", "condition_value":["1", "10"]}

        These are the available conditions:

        >>> "==", "!=", ">=", ">", "<", "<="

        If you are looking to combine your filters with multiple ORs, simply add the following inside the query {"strict":"must_or"}.

        Parameters
        ----------
        dataset_id: string
            Unique name of dataset
        select_fields: list
            Fields to include in the search results, empty array/list means all fields.
        cursor: string
            Cursor to paginate the document retrieval
        page_size: int
            Size of each page of results
        include_vector: bool
            Include vectors in the search results
        sort: list
            Fields to sort by. For each field, sort by descending or ascending. If you are using descending by datetime, it will get the most recent ones.
        filters: list
            Query for filtering the search results
        is_random: bool
            If True, retrieves doucments randomly. Cannot be used with cursor.
        random_state: int
            Random Seed for retrieving random documents.
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/get_where",
            method="POST",
            parameters={
                "select_fields": select_fields,
                "cursor": cursor,
                "page_size": page_size,
                "sort": sort,
                "include_vector": include_vector,
                "filters": filters,
                "random_state": random_state,
                "is_random": is_random,
            },
        )

    def paginate(
        self,
        dataset_id: str,
        page: int = 1,
        page_size: int = 20,
        include_vector: bool = True,
        select_fields: list = [],
    ):

        """
        Retrieve documents with filters and support for pagination. \n
        For more information about filters check out datasets.documents.get_where.

        Parameters
        ----------
        dataset_id: string
            Unique name of dataset
        page: int
            Page of the results
        page_size: int
            Size of each page of results
        include_vector: bool
            Include vectors in the search results
        select_fields: list
            Fields to include in the search results, empty array/list means all fields.
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/paginate",
            parameters={
                "page": page,
                "page_size": page_size,
                "include_vector": include_vector,
                "select_fields": select_fields,
            },
        )

    def update(self, dataset_id: str, update: dict, insert_date: bool = True):

        """
        Edits documents by providing a key value pair of fields you are adding or changing, make sure to include the "_id" in the documents. \n
        For update multiple documents refer to datasets.documents.bulk_update

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        update : list
            A dictionary to edit and add fields to a document. It should be specified in a format of {"field_name": "value"}. e.g. {"item.status" : "Sold Out"}
        insert_date	: bool
            Whether to include insert date as a field 'insert_date_'.

        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/update",
            method="POST",
            parameters={"update": update, "insert_date": insert_date},
        )

    def update_where(self, dataset_id: str, update: dict, filters: list = []):

        """
        Updates documents by filters. The updates to make to the documents that is returned by a filter. \n
        For more information about filters refer to datasets.documents.get_where.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        update : list
            A dictionary to edit and add fields to a document. It should be specified in a format of {"field_name": "value"}. e.g. {"item.status" : "Sold Out"}
        filters: list
            Query for filtering the search results

        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/update_where",
            method="POST",
            parameters={"update": update, "filters": filters},
        )

    def bulk_update(
        self,
        dataset_id: str,
        updates: list,
        insert_date: bool = True,
        return_documents: bool = False,
    ):

        """
        Edits documents by providing a key value pair of fields you are adding or changing, make sure to include the "_id" in the documents.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        updates : list
            Updates to make to the documents. It should be specified in a format of {"field_name": "value"}. e.g. {"item.status" : "Sold Out"}
        insert_date	: bool
            Whether to include insert date as a field 'insert_date_'.
        include_updated_ids	: bool
            Include the inserted IDs in the response

        """

        base_url = self.config.get_option("api.base_ingest_url")

        if return_documents is False:
            return self.make_http_request(
                endpoint=f"/datasets/{dataset_id}/documents/bulk_update",
                method="POST",
                parameters={"updates": updates, "insert_date": insert_date},
                base_url=base_url,
            )
        else:
            response_json = self.make_http_request(
                endpoint=f"/datasets/{dataset_id}/documents/bulk_update",
                method="POST",
                parameters={"updates": updates, "insert_date": insert_date},
                base_url=base_url,
            )

            try:
                status_code = response_json.status_code
            except:
                status_code = 200

            return {
                "response_json": response_json,
                "documents": updates,
                "status_code": status_code,
            }

    def delete(self, dataset_id: str, id: str):

        """
        Delete a document by ID. \n
        For deleting multiple documents refer to datasets.documents.bulk_delete

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        id : string
            ID of document to delete
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/delete",
            method="POST",
            parameters={"id": id},
        )

    def delete_where(self, dataset_id: str, filters: list):

        """
        Delete a document by filters. \n
        For more information about filters refer to datasets.documents.get_where.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        filters: list
            Query for filtering the search results
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/delete_where",
            method="POST",
            parameters={"filters": filters},
        )

    def bulk_delete(self, dataset_id: str, ids: list = []):

        """
        Delete a list of documents by their IDs.

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        ids : list
            IDs of documents to delete
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/bulk_delete",
            method="POST",
            parameters={"ids": ids},
        )

    def delete_fields(self, dataset_id: str, id: str, fields: list):

        """
        Delete fields in a document in a dataset by its id

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        id : string
            ID of a document in a dataset
        fields: list
            List of fields to delete in a document
        """

        return self.make_http_request(
            endpoint=f"/datasets/{dataset_id}/documents/delete_fields",
            method="POST",
            parameters={"id": id, "fields": fields},
        )
