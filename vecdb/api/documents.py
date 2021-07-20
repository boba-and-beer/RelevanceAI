from ..base import Base

class Documents(Base):
    def __init__(self, project, api_key, base_url):
        self.project = project
        self.api_key = api_key
        self.base_url = base_url
        
    def list(self, dataset_id: str, cursor: str=None, page_size: int=20,
        sort: list=[], include_vector: bool=True, random_state: int=0):
        return self.make_http_request(
            endpoint=f"datasets/{dataset_id}/documents/list", 
            method="GET",
            parameters={
                "cursor": cursor,
                "page_size": page_size,
                "sort": sort,
                "include_vector": include_vector,
                "random_state": random_state
            })
    
    def get(self, dataset_id: str, id: str, select_fields: list=[],
        cursor: str=None, page_size: int=20, sort: list=[],
        include_vector: bool=True, output_format: str = "json"):
        return self.make_http_request(
            endpoint=f"datasets/{dataset_id}/documents/get",
            parameters={
                "id": id,
                "select_fields": select_fields,
                "cursor": cursor,
                "page_size": page_size,
                "sort": sort,
                "include_vector": include_vector
            }
        )

    def get_where(self, dataset_id: str, filters: list=[], cursor: str=None,
        page_size: int=20, sort: list=[], select_fields: list=[], 
        include_vector: bool=True, random_state: int = 0, 
        is_random: bool=False, output_format: str="json"):
        return self.make_http_request(
            endpoint=f"datasets/{dataset_id}/documents/get_where", 
            method="POST", 
            parameters={
                "select_fields": select_fields,
                "cursor": cursor,
                "page_size": page_size,
                "sort": sort,
                "include_vector": include_vector,
                "filters": filters,
                "random_state": random_state,
                "is_random": is_random}
            , output_format = output_format)
    
    def bulk_update(self, dataset_id: str, updates: list):
        return self.make_http_request(
            endpoint=f"datasets/{dataset_id}/documents/bulk_update",
            method="POST",
            parameters={
                "updates": updates
            }
        )
    

    def get_where_all(self, dataset_id: str, chunk_size: int = 10000, filters: list=[], sort: list=[], select_fields: list=[], include_vector: bool=True, random_state: int = 0, output_format: str = "json"):
        #Initialise values
        length = 1
        cursor = None
        full_data = []

        #While there is still data to fetch, fetch it at the latest cursor
        while length > 0 :
            x = self.get_where(dataset_id, filters=filters, cursor=cursor, page_size= chunk_size, sort = sort, select_fields = select_fields, include_vector = include_vector, random_state = random_state, output_format = output_format)
            length = len(x['documents'])
            cursor = x['cursor']

            #Append fetched data to the full data
            if length > 0:
                [full_data.append(i) for i in x['documents']]
        
        return full_data
