import logging
from io import IOBase
from typing import List

import semantha_sdk
import streamlit as st
from semantha_sdk.model.document_class import DocumentClass
from semantha_sdk.model.document_information import DocumentInformation


class SemanthaConnector:

    __STOP_TOKENS = ["References:", "Reference:"]

    def __init__(self, server, key, domain):
        logging.info("Authenticating semantha ...")
        self.__sdk = semantha_sdk.login(
            server_url=server, key=key
        )
        self.__domain = domain
        logging.info("... successful!")

    def compare_to_library(self, in_file: IOBase, threshold: float):
        return self.__sdk.domains(domainname=self.__domain).references.post(
            file=in_file,
            similaritythreshold=threshold,
            maxreferences=1
        )

    @st.cache_data(show_spinner=False)
    def get_text_of_library_paragraph(_self, doc_id: str, par_id: str) -> str:
        return _self.__sdk.domains(domainname=_self.__domain)\
            .referencedocuments(documentid=doc_id).paragraphs(id=par_id).get().text

    @st.cache_data(show_spinner=False)
    def get_tags_of_library_document(_self, doc_id: str) -> List[str]:
        __tags = _self.__sdk.domains(domainname=_self.__domain).referencedocuments(documentid=doc_id).get().tags
        __derived_tags = _self.__sdk.domains(domainname=_self.__domain)\
            .referencedocuments(documentid=doc_id).get().derived_tags
        return __tags + __derived_tags

    @st.cache_data(show_spinner=False)
    def get_library_tags(_self) -> List[str]:
        return _self.__sdk.domains(domainname=_self.__domain).tags.get()

    @st.cache_data(show_spinner=False)
    def get_library_entries_for_tag(_self, tag) -> List[DocumentInformation]:
        return _self.__sdk.domains(domainname=_self.__domain).referencedocuments.get(
            tags=tag, fields="id,name,contentpreview"
        ).data

    @st.cache_data(show_spinner=False)
    def get_category_of_document(_self, doc_id: str) -> DocumentClass:
        return _self.__sdk.domains(domainname=_self.__domain).referencedocuments(documentid=doc_id).get().document_class

    @st.cache_data(show_spinner=False)
    def get_category_by_id(_self, category_id: str) -> DocumentClass:
        return _self.__sdk.domains(domainname=_self.__domain).documentclasses(id=category_id).get()

    @st.cache_data(show_spinner=False)
    def generate_retrieval_augmented_answer(_self, question: str):
        return _self.__sdk.domains(domainname=_self.__domain).answers.post(
            question=question,
            maxreferences=5,
            similaritythreshold=0.4
        )

    @st.cache_data(show_spinner=False)
    def summarize(_self, sources: List[str], topic: str) -> str:
        __sources_with_refs = [f"[{i + 1}] {s}" for i, s in enumerate(sources)]
        resp = _self.__sdk.domains(domainname=_self.__domain).summarizations.post(
            topic=topic,
            texts=__sources_with_refs
        )
        for token in _self.__STOP_TOKENS:
            resp = resp.split(token, maxsplit=1)[0]
        return resp.strip()
