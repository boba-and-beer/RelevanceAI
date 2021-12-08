import scipy.spatial.distance as spatial_distance
from relevanceai.base import Base
from doc_utils.doc_utils import DocUtils
from relevanceai.vector_tools.constants import NEAREST_NEIGHBOURS

doc_utils = DocUtils()

class NearestNeighbours(Base, DocUtils):

    def __init__(self, project, api_key):
        self.project = project
        super().__init__(project, api_key)

    @staticmethod
    def get_nearest_neighbours(
        docs: list, 
        vector: list,
        vector_field: str,
        distance_measure_mode: NEAREST_NEIGHBOURS= 'cosine', 
        callable_distance = None
        ): 

        if callable_distance:
            sort_key = [callable_distance(i, vector) for i in doc_utils.get_field_across_documents(vector_field, docs)]

        elif distance_measure_mode == 'cosine':
            sort_key = [spatial_distance.cosine(i, vector) for i in doc_utils.get_field_across_documents(vector_field, docs)]

        elif distance_measure_mode == 'l2':
            sort_key = [spatial_distance.euclidean(i, vector) for i in doc_utils.get_field_across_documents(vector_field, docs)]

        else:
            raise ValueError('Need valid distance measure mode or callable distance')

        doc_utils.set_field_across_documents('nearest_neighbour_distance', sort_key, docs)

        return sorted(docs, key=lambda x: x['nearest_neighbour_distance'])

    