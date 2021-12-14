from random import randint
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from sklearn import preprocessing
from tqdm.auto import tqdm
from typing import List
from doc_utils import DocUtils
from relevanceai.logger import LoguruLogger
from relevanceai.api.client import BatchAPIClient
from relevanceai.vector_tools.cluster import KMeans
from relevanceai.data_tools.base_text_processing import BaseTextProcessing
from relevanceai.vector_tools.dim_reduction import Ivis
from ivis import Ivis


class PlotTextThemeModel(BatchAPIClient, BaseTextProcessing, LoguruLogger, DocUtils):
    def __init__(
        self,
        project: str,
        api_key: str,
        # dataset_info
        dataset_id: str,
        upload_chunksize: int = 50,
        # clustering
        cluster_field: str = "_cluster_",
        # dimensionality reduction parameters
        embedding_dims: int = 2,
        dim_red_k: int = 800,
        n_epochs_without_progress: int = 100,
        # nlp parameters
        language: str = "english",
    ):
        self.dataset_id = dataset_id
        self.upload_chunksize = upload_chunksize
        self.cluster_field = cluster_field
        self.embedding_dims = embedding_dims
        self.dim_red_k = dim_red_k
        self.n_epochs_without_progress = n_epochs_without_progress
        self.language = language
        super().__init__(project, api_key)

    def build_and_plot_clusters(
        self,
        vector_field: str,
        text_field: str,
        max_doc_num: int = None,
        k: int = 10,
        alias: str = "kmeans",
        lower: bool = True,
        remove_digit: bool = True,
        remove_punct: bool = True,
        remove_stop_words: bool = True,
        additional_stop_words: List[str] = [],
        cluster_representative_cnt: int = 3,
        plot_axis: str = "off",
        figsize: Tuple[int, ...] = (20, 10),
        cmap: str = "plasma",
        alpha: float = 0.2,
    ):
        # get documents
        docs = self.get_documents(
            vector_field=vector_field, text_field=text_field, max_doc_num=max_doc_num
        )

        # perform kmeans clustering
        alias = alias + "_" + str(k)
        centers, clustered_docs = self.kmeans_clustering(
            docs=docs, vector_field=vector_field, k=k, alias=alias
        )
        for i, cl_doc in enumerate(tqdm(clustered_docs)):
            docs[i]["_".join([self.cluster_field, vector_field, alias])] = cl_doc[
                self.cluster_field
            ][vector_field][alias]

        # get cluster data
        cluster_data = self.get_cluster_datafield(
            docs=docs,
            vector_field=vector_field,
            text_field=text_field,
            alias=alias,
            lower=lower,
            remove_digit=remove_digit,
            remove_punct=remove_punct,
        )
        clusters_top_n_words = self.get_cluster_word_freq(
            cluster_data=cluster_data,
            remove_stop_words=remove_stop_words,
            additional_stop_words=additional_stop_words,
            cluster_representative_cnt=cluster_representative_cnt,
        )
        for c in clusters_top_n_words:
            self.logger.info(c, clusters_top_n_words[c])

        # dimensionality reduction
        # 1) Fit the model and reduce vector size
        vectors = self.get_field_across_documents(vector_field, docs)
        dr_docs = self.dim_reduction(
            vector_data=vectors,
            embedding_dims=self.embedding_dims,
            k=self.dim_red_k,
            n_epochs_without_progress=self.n_epochs_without_progress,
        )
        for i, dr in enumerate(dr_docs):
            docs[i][vector_field + "_dr_vector_"] = dr.tolist()
        # 2) reduce center vector size
        vectors = [c["centroid_vector_"] for c in centers]
        dr_centers = self.dim_reduction(
            vector_data=vectors,
            embedding_dims=self.embedding_dims,
            k=self.dim_red_k,
            n_epochs_without_progress=self.n_epochs_without_progress,
            run_fit=False,
        )
        for i, c in enumerate(centers):
            c["centroid_dr_vector_"] = dr_centers[i]

        # plot
        self.plot_clusters(
            docs,
            dr_docs,
            centers,
            cluster_data,
            vector_field,
            alias,
            cluster_representative_cnt,
            plot_axis=plot_axis,
            figsize=figsize,
            cmap=cmap,
            alpha=alpha,
        )

    def get_documents(
        self, vector_field: str, text_field: str, max_doc_num: int = None
    ):
        self.logger.info(" * Loading documents")
        filters = [
            {
                "field": vector_field,
                "filter_type": "exists",
                "condition": "==",
                "condition_value": " ",
            }
        ]
        fields = [vector_field, text_field]
        if max_doc_num:
            page_size = 200 if max_doc_num > 200 else max_doc_num
            batch_doc = self.batch_load_docs(
                fields=fields, filters=filters, page_size=page_size
            )
            docs = batch_doc["documents"]
            cursor = batch_doc["cursor"]
            while batch_doc["documents"] != [] and len(docs) > max_doc_num - page_size:
                batch_doc = self.batch_load_docs(
                    fields=fields, filters=filters, page_size=page_size, cursor=cursor
                )
                docs.extend(batch_doc["documents"])
        else:
            docs = self.get_all_documents(
                dataset_id=self.dataset_id, filters=filters, select_fields=fields
            )
        return docs

    def batch_load_docs(
        self,
        fields: List[str],
        filters: List[dict] = [],
        page_size: int = 200,
        cursor: str = None,
    ):
        return self.datasets.documents.get_where(
            dataset_id=self.dataset_id,
            select_fields=fields,
            page_size=page_size,
            filters=filters,
            cursor=cursor,
        )

    def kmeans_clustering(
        self, docs, vector_field=str, k: int = 10, alias: str = "kmeans"
    ):
        self.logger.info(" * Kmeans Clustering")
        clusterer = KMeans(k=k)
        clustered_docs = clusterer.fit_documents([vector_field], docs, alias=alias)
        res = self.update_documents(
            self.dataset_id, clustered_docs, chunksize=self.upload_chunksize
        )
        centers = clusterer.get_centroid_docs()
        self.services.cluster.centroids.insert(
            dataset_id=self.dataset_id,
            cluster_centers=centers,
            vector_field=vector_field,
            alias=alias,
        )
        return centers, clustered_docs

    @staticmethod
    def get_field_value_by_id(docs: List[dict], id: str, field: str):
        for doc in docs:
            if doc["_id"] == id:
                return DocUtils.get_field(field, doc)

    def get_cluster_datafield(
        self,
        docs: List[dict],
        vector_field: str,
        text_field: str,
        alias: str,
        lower: bool = True,
        remove_digit: bool = True,
        remove_punct: bool = True,
    ):
        self.logger.info(" * Extracting cluster info")
        cluster_data = {}
        for i, doc in tqdm(enumerate(docs)):
            cluster_name = doc["_".join([self.cluster_field, vector_field, alias])]
            if cluster_name not in cluster_data:
                cluster_data[cluster_name] = {"data": []}
            text = self.normalize_text(
                txt=self.get_field_value_by_id(docs, id=doc["_id"], field=text_field),
                lower=lower,
                remove_digit=remove_digit,
                remove_punct=remove_punct,
            )
            cluster_data[cluster_name]["data"].append(text)
        return cluster_data

    @staticmethod
    def get_cluster_population(cluster_data: dict):
        return [
            (cluster_name, len(v["data"])) for cluster_name, v in cluster_data.items()
        ]

    def get_cluster_word_freq(
        self,
        cluster_data: dict,
        remove_stop_words: bool = True,
        additional_stop_words: List[str] = [],
        cluster_representative_cnt: int = 3,
    ):
        for cluster in tqdm(cluster_data):
            cluster_data[cluster]["word_freq"] = self.get_word_frequency(
                str_list=cluster_data[cluster]["data"],
                remove_stop_words=remove_stop_words,
                additional_stop_words=additional_stop_words,
                language=self.language,
            )
        return {
            c: [cluster_data[c]["word_freq"][:cluster_representative_cnt]]
            for c in cluster_data
        }

    def dim_reduction(
        self,
        vector_data: List,
        embedding_dims=2,
        k=800,
        n_epochs_without_progress=100,
        run_fit=True,
    ):
        self.logger.info(" * Dimensionality reduction")
        vector_data = np.array(vector_data)
        if run_fit:
            self.dr_model = Ivis(
                embedding_dims=embedding_dims,
                k=k,
                n_epochs_without_progress=n_epochs_without_progress,
            )
            dr_docs = self.dr_model.fit_transform(vector_data)
        else:
            dr_docs = self.dr_model.transform(vector_data)
        return dr_docs

    def plot_clusters(
        self,
        docs: List[dict],
        dr_docs: List,
        centers: List[dict],
        cluster_data: dict,
        vector_field: str,
        alias: str,
        cluster_representative_cnt: int,
        plot_axis: str = "off",
        figsize: Tuple[int, ...] = (20, 10),
        cmap: str = "plasma",
        alpha: float = 0.2,
    ):
        group = [x["_".join([self.cluster_field, vector_field, alias])] for x in docs]
        le = preprocessing.LabelEncoder()
        color = le.fit_transform(group)

        plt.axis(plot_axis)
        plt.figure(figsize=figsize)
        plt.scatter(
            [x[0] for x in dr_docs],
            [x[1] for x in dr_docs],
            c=color,
            cmap=cmap,
            alpha=alpha,
        )

        for i, r in enumerate(centers):
            plt.annotate(
                [
                    x[0]
                    for x in cluster_data[r["_id"]]["word_freq"][
                        :cluster_representative_cnt
                    ]
                ],
                (r["centroid_dr_vector_"][0] - 0.5, r["centroid_dr_vector_"][1]),
            )


def build_and_plot_clusters(
    self,
    project: str,
    api_key: str,
    dataset_id: str,
    vector_field: str,
    text_field: str,
    upload_chunksize: int = 50,
    cluster_field: str = "_cluster_",
    embedding_dims: int = 2,
    dim_red_k: int = 800,
    n_epochs_without_progress: int = 100,
    language: str = "english",
    max_doc_num: int = None,
    k: int = 10,
    alias: str = "kmeans",
    lower: bool = True,
    remove_digit: bool = True,
    remove_punct: bool = True,
    remove_stop_words: bool = True,
    additional_stop_words: List[str] = [],
    cluster_representative_cnt: int = 3,
    plot_axis: str = "off",
    figsize: Tuple[int, ...] = (20, 10),
    cmap: str = "plasma",
    alpha: float = 0.2,
):
    model = PlotTextThemeModel(
        project=project,
        api_key=api_key,
        dataset_id=dataset_id,
        upload_chunksize=upload_chunksize,
        # clustering
        cluster_field=cluster_field,
        # dimensionality reduction parameters
        embedding_dims=embedding_dims,
        dim_red_k=dim_red_k,
        n_epochs_without_progress=n_epochs_without_progress,
        language=language,
    )
    return model.build_and_plot_clusters(
        vector_field=vector_field,
        text_field=text_field,
        max_doc_num=max_doc_num,
        k=k,
        alias=alias,
        lower=lower,
        remove_digit=remove_digit,
        remove_punct=remove_punct,
        remove_stop_words=remove_stop_words,
        additional_stop_words=additional_stop_words,
        cluster_representative_cnt=cluster_representative_cnt,
        plot_axis=plot_axis,
        figsize=figsize,
        cmap=cmap,
        alpha=alpha,
    )