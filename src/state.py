import logging

import streamlit as st
from semantha_sdk.model.document import Document

from semantha import SemanthaConnector
from snowpark_connection import SnowparkConnector

CONST_HIGH_SIM = 0.95
CONST_MID_SIM = 0.80
CONST_HIGH_SIM_COLOR = "#95C23D"
CONST_MID_SIM_COLOR = "#FDD835"
CONST_LOW_SIM_COLOR = "#CCCCCC"
NO_TAG = "(no tag)"

__semantha = None
__snowpark = None


def __init_page_id():
    if "__page_id" not in st.session_state:
        logging.info("No state for 'page_id' found, initializing with '1'.")
        st.session_state.__page_id = 1


def __init_documents_with_references():
    #  -> list[str]
    if "__documents_with_references" not in st.session_state:
        logging.info("No state for 'documents_with_references' found, initializing with empty list.")
        st.session_state.__documents_with_references = []


def __init_similarity_threshold():
    if "__similarity_threshold" not in st.session_state:
        logging.info("No state for 'similarity_threshold' found, initializing with '0.0'.")
        st.session_state.__similarity_threshold = 0.0


def __init_selected_tags_compare_view():
    if "__selected_tags_compare_view" not in st.session_state:
        logging.info("No state for 'selected_tags_compare_view' found, initializing with empty list.")
        st.session_state.__selected_tags_compare_view = []


def __init_docs_with_refs_with_tags():
    if "__docs_with_refs_with_tags" not in st.session_state:
        logging.info("No state for '__docs_with_refs_with_tags' found, initializing with empty dict.")
        st.session_state.__docs_with_refs_with_tags = {}


def __init_single_document_with_references():
    if "__single_document_with_references" not in st.session_state:
        logging.info("No state for '__single_document_with_references' found, initializing with empty tuple.")
        st.session_state.__single_document_with_references = (None, None)


def __init_default_sf_credentials_enabled():
    if "__default_sf_credentials_enabled" not in st.session_state:
        logging.info("No state for '__default_sf_credentials_enabled' found, initializing with True.")
        st.session_state.__default_sf_credentials_enabled = True


def __init_snowflake_cred_dict():
    if "__snowflake_cred_dict" not in st.session_state:
        logging.info("No state for '__snowflake_cred_dict' found, initializing dict with None values.")
        st.session_state.__snowflake_cred_dict = {
            'account': None,
            'user': None,
            'password': None,
            'role': None,
            'warehouse': None,
            'database': None,
            'schema': None,
            'stage': None
        }


def __init_tag_for_summarization():
    if "__tag_for_summarization" not in st.session_state:
        logging.info("No state for '__tag_for_summarization' found, initializing with 'None'.")
        st.session_state.__tag_for_summarization = None


@st.cache_resource(show_spinner=False)
def get_semantha() -> SemanthaConnector:
    global __semantha
    if __semantha is None:
        logging.warning("SemanthaConnector is None, recreating...")
        semantha = st.secrets.semantha
        __semantha = SemanthaConnector(semantha.server_url, semantha.api_key,
                                       semantha.domain)
    return __semantha


@st.cache_resource(show_spinner=False)
def get_snowpark() -> SnowparkConnector:
    global __snowpark
    if __snowpark is None:
        logging.warning("SnowparkConnector is None, recreating...")
        __snowpark = SnowparkConnector(**get_snowflake_cred_dict())
    return __snowpark


def set_page_id(page_id: int):
    __init_page_id()
    st.session_state.__page_id = int(page_id)


def get_page_id():
    __init_page_id()
    return st.session_state.__page_id


def set_similarity_threshold(threshold: float):
    __init_similarity_threshold()
    st.session_state.__similarity_threshold = threshold


def get_similarity_threshold():
    __init_similarity_threshold()
    return st.session_state.__similarity_threshold


def add_document_with_references(doc: Document):
    __init_documents_with_references()
    st.session_state.__documents_with_references.append(doc)


def get_documents_with_references():
    __init_documents_with_references()
    return st.session_state.__documents_with_references


def reset_documents_with_references():
    __init_documents_with_references()
    st.session_state.__documents_with_references = []


def set_selected_tags_compare_view(tags):
    __init_selected_tags_compare_view()
    st.session_state.__selected_tags_compare_view = tags


def get_selected_tags_compare_view():
    __init_selected_tags_compare_view()
    return st.session_state.__selected_tags_compare_view


def set_docs_with_refs_with_tags(doc_dict: dict):
    __init_docs_with_refs_with_tags()
    st.session_state.__docs_with_refs_with_tags = doc_dict


def get_docs_with_refs_with_tags():
    __init_docs_with_refs_with_tags()
    return st.session_state.__docs_with_refs_with_tags


def reset_docs_with_refs_with_tags():
    __init_docs_with_refs_with_tags()
    st.session_state.__docs_with_refs_with_tags = {}


def set_single_document_with_references(doc_name: str, document):
    __init_single_document_with_references()
    st.session_state.__single_document_with_references = (doc_name, document)


def get_single_document_with_references():
    __init_single_document_with_references()
    return st.session_state.__single_document_with_references


def reset_single_document_with_references():
    __init_single_document_with_references()
    st.session_state.__single_document_with_references = (None, None)


def get_snowflake_cred_dict():
    __init_snowflake_cred_dict()
    return st.session_state.__snowflake_cred_dict


def set_snowflake_cred_dict(snowflake_credentials_as_dict):
    __init_snowflake_cred_dict()
    st.session_state.__snowflake_cred_dict = snowflake_credentials_as_dict


def get_default_sf_credentials_enabled():
    __init_default_sf_credentials_enabled()
    return st.session_state.__default_sf_credentials_enabled


def set_default_sf_credentials_enabled(enabled: bool):
    __init_default_sf_credentials_enabled()
    st.session_state.__default_sf_credentials_enabled = enabled


def get_tag_for_summarization():
    __init_tag_for_summarization()
    return st.session_state.__tag_for_summarization


def set_tag_for_summarization(tag: str):
    __init_tag_for_summarization()
    st.session_state.__tag_for_summarization = tag
