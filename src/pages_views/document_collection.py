import base64
import logging

import numpy as np
import pandas as pd
import streamlit as st

import state
from pages_views.abstract_pages import AbstractContentPage
from util.semantha_model_handling import get_paragraph_matches_of_doc
from util.text_handling import short_text


class DocumentCollection(AbstractContentPage):

    def __init__(self, page_id: int):
        super().__init__()
        if page_id == 3:
            self._content_placeholder = st.container()
        else:
            self._content_placeholder = st.empty()
        self.__tags = state.get_semantha().get_library_tags()

    def _display_content(self, max_fetch: int = 100, max_files: int = 20):
        sf_settings = state.get_snowflake_cred_dict()
        for v in sf_settings.values():
            if not v:
                st.error("At least one field of the streamlit account information is empty. "
                         "Please fill in all account information before you proceed.")
                return
        # limit fetching of list of documents from snowflake to the first 100 documents
        __file_list = state.get_snowpark().get_list_of_file_names(max_fetch)
        if __file_list is not None:
            __files_to_display = []
            for f in __file_list:
                doc = FileDocument(f)
                # limit downloading of documents from snowflake to the first 20 documents
                if len(__files_to_display) == max_files:
                    break
                if doc.is_analyzable():
                    __files_to_display.append(doc)
                else:
                    logging.debug(f"Found non analyzable file '{doc.path}'")
            self._display_files(__files_to_display)
        self.__display_analysis_overview()
        __tag_for_summarization = state.get_tag_for_summarization()
        if __tag_for_summarization is not None:
            self.__display_summarization(__tag_for_summarization)
        self.__display_analysis_result()

    def _display_files(self, documents):
        __selected_file = None
        for d in documents:
            if d.is_viewable():
                __selected_file = d
                break
        with st.expander(label="Document Collection", expanded=True):
            st.write("Below you can find your documents from your Snowflake data collection. "
                     "A document preview can be activated by clicking on the arrow icon on the left side. "
                     "Please note that only the first 20 documents are displayed in this demo.")
            __list_col, __pv_col = st.columns(2)
            __doc_container = __list_col.container()
            for i, doc in enumerate(documents):
                __but_col, __doc_col = __doc_container.columns([0.8, 10])
                __curr_file_name = doc.get_name()
                with __doc_col.container():
                    st.info(__curr_file_name)
                __viewable = doc.is_viewable()
                __view_button = __but_col.button('↗️', disabled=not __viewable, key=f'open_doc_{i}',
                                                 help="Switch file preview")
                if __view_button:
                    __selected_file = doc
            with __pv_col.container():
                self.__display_pdf(__selected_file)
        _, _, __bc, _, _ = st.columns(5)
        __analyze_button = __bc.button('Analyze Document Collection', disabled=False, key='analyze_button')
        if __analyze_button:
            self.__analyze_doc_collection(documents)

    def __display_analysis_overview(self):
        __docs_with_refs_with_tags = state.get_docs_with_refs_with_tags()
        if len(__docs_with_refs_with_tags) > 0:
            __matched_tags = self.__determine_all_matched_tag(__docs_with_refs_with_tags)
            with st.expander(label="Document Collection Overview", expanded=True):
                __doc_col, __tag_col = st.columns([1, 2])
                with __doc_col.container():
                    st.write("lorem ipsum")
                __matched_tags__list = [key for key in __matched_tags]
                if len(__matched_tags__list) > 0:
                    __number_items_per_row = 6
                    __chars_per_line = 30
                    __tag_list = sorted(__matched_tags__list)
                    __rows = int(np.ceil(len(self.__tags) / __number_items_per_row))
                with __tag_col.container():
                    for k in range(__rows):
                        __bu_cols = st.columns([1] * __number_items_per_row)
                        for j in range(__number_items_per_row):
                            if k * __number_items_per_row + j < len(self.__tags):
                                __tag = self.__tags[k * __number_items_per_row + j]
                                if __tag in __tag_list:
                                    __b = __bu_cols[j].button(
                                        short_text(__tag, __chars_per_line),
                                        key=f"overview_{__tag}",
                                        help=f"Create summary for topic '{__tag}'",
                                    )
                                else:
                                    __b = __bu_cols[j].button(
                                        short_text(__tag, __chars_per_line),
                                        key=f"overview_{__tag}",
                                        disabled=True,
                                    )

    def __display_analysis_result(self):
        if len(state.get_docs_with_refs_with_tags()) > 0:
            __selected_tag = None
            __selected_doc = None
            with st.expander(label="Analysis Result", expanded=True):
                for i, (name, refs) in enumerate(
                        state.get_docs_with_refs_with_tags().items()
                ):
                    if i > 0:
                        st.divider()
                    __tag_list = []
                    for r in refs:
                        for v in r.values():
                            __tag = v["tag"]
                            if __tag not in __tag_list:
                                __tag_list.append(__tag)
                    __doc_col, __tag_col = st.columns([1, 2])
                    with __doc_col.container():
                        __analyze_button_col, __doc_name_col = st.columns([0.2, 2])
                        with __doc_name_col.container():
                            st.info(name)
                        __single_doc_analysis_button = __analyze_button_col.button(
                            "📑",
                            key=f'sdab_{name}',
                            disabled=len(__tag_list) == 0,
                            help="Use this for manual analysis. __Hint__: You have to select the the tab 'Individual Document' afterwards."
                        )
                        if __single_doc_analysis_button:
                            __selected_doc = name
                            __doc = None
                            for d in state.get_documents_with_references():
                                if d.name == name:
                                    __doc = d
                            if __doc is not None:
                                state.set_single_document_with_references(name, __doc)
                    if len(__tag_list) > 0:
                        __number_items_per_row = 6
                        __chars_per_line = 30
                        __tag_list = sorted(__tag_list)
                        __rows = int(np.ceil(len(self.__tags) / __number_items_per_row))
                        with __tag_col.container():
                            for k in range(__rows):
                                __bu_cols = st.columns([1] * __number_items_per_row)
                                for j in range(__number_items_per_row):
                                    if k * __number_items_per_row + j < len(self.__tags):
                                        __tag = self.__tags[k * __number_items_per_row + j]
                                        if __tag in __tag_list:
                                            __b = __bu_cols[j].button(
                                                short_text(__tag, __chars_per_line),
                                                key=f"{name}_{__tag}",
                                                help=f"Create summary for topic '{__tag}'",
                                            )
                                        else:
                                            __b = __bu_cols[j].button(
                                                short_text(__tag, __chars_per_line),
                                                key=f"{name}_{__tag}",
                                                disabled=True,
                                            )
                                        if __b:
                                            __selected_tag = __tag
            state.set_tag_for_summarization(__selected_tag)

    @st.cache_data(show_spinner=False)
    def __determine_all_matched_tag(_self, docs_with_refs_with_tags):
        matched_tags = {}
        for _, refs in docs_with_refs_with_tags.items():
            for r in refs:
                for v in r.values():
                    __tag = v["tag"]
                    if __tag in matched_tags:
                        matched_tags[__tag] += 1
                    else:
                        matched_tags[__tag] = 1
        return matched_tags

    def __analyze_doc_collection(self, documents):
        state.reset_documents_with_references()
        state.reset_docs_with_refs_with_tags()
        progress_text = "Comparing document collection with references. This will take some time!"
        my_bar = st.progress(0.0, text=progress_text)
        increment = 1 / len(documents)
        for i, doc in enumerate(documents):
            __curr_file_name = doc.get_name()
            my_bar.progress((i + 1) * increment, text=f"{progress_text} Processing file '{__curr_file_name}'")
            state.add_document_with_references(state.get_semantha().compare_to_library(in_file=doc.as_stream(),
                                                                                       threshold=state.get_similarity_threshold()))
        with st.spinner("Analyzing topics."):
            __docs_with_tags = {}
            for doc in state.get_documents_with_references():
                __matches = get_paragraph_matches_of_doc(doc)
                __matches_with_tags = []
                for m in __matches:
                    __matches_with_tags.append({
                        m[0].id: {
                            'ref': m[1][0],
                            'tag': state.get_semantha().get_tags_of_library_document(m[1][0].document_id)[0]
                        }
                    })
                __docs_with_tags[doc.name] = __matches_with_tags
            state.set_docs_with_refs_with_tags(__docs_with_tags)
            st.success("Analysis of document collection is done. Results are shown below.")

    def __display_summarization(self, tag):
        __seen_par_ids = []
        with st.expander(label=f"Summarization for Topic '{tag}'", expanded=True):
            with st.spinner("Generating the summary..."):
                __sources = []
                __docs_with_refs = state.get_documents_with_references()
                __docs_with_refs_with_tags = state.get_docs_with_refs_with_tags()
                __relevant_sections = []
                for doc_name, refs in state.get_docs_with_refs_with_tags().items():
                    for r in refs:
                        for ref_id, v in r.items():
                            if v["tag"] == tag:
                                for input_doc in __docs_with_refs:
                                    if input_doc.name == doc_name:
                                        __visited_paragraphs = []
                                        __delayed_break = False
                                        for page in input_doc.pages:
                                            if page.contents is not None:
                                                for content in page.contents:
                                                    if content.paragraphs is not None:
                                                        for p in content.paragraphs:
                                                            __visited_paragraphs.append(p)
                                                            if __delayed_break:
                                                                break
                                                            if p.id == ref_id:
                                                                __delayed_break = True
                                                    if __delayed_break:
                                                        break
                                            if __delayed_break:
                                                break
                                        __relevant_sections.append(
                                            ("\n".join(p.text for p in __visited_paragraphs[-3:]), doc_name))
                __sources = [p for p, _ in __relevant_sections]
                __summarization = state.get_semantha().summarize(__sources, tag)
                if __summarization is not None:
                    st.write(__summarization)
                    __df = pd.DataFrame.from_records([[p, doc] for p, doc in __relevant_sections], columns=["Reference", "Document"])
                    __df.index = np.arange(1, len(__df) + 1)
                    st.dataframe(__df, use_container_width=True)
                else:
                    st.error("Unfortunately no summary could be generate for the given documents!")

    @staticmethod
    def __display_pdf(document):
        if document is None:
            st.error("None of the provided documents can be displayed. Currently, only PDF document display is supported.")
        pdf_display = F'<center><iframe src="data:application/pdf;base64,{document.as_base64()}" width="600" height="800" type="application/pdf"></iframe></center>'
        st.markdown(pdf_display, unsafe_allow_html=True)


class FileDocument:
    def __init__(self, path: str):
        self.path = path

    def get_name(self):
        return self.path.split("/")[-1]

    def is_viewable(self):
        return self.path.endswith(".pdf")

    def is_analyzable(self):
        return self.path.endswith(".pdf") or self.path.endswith(".txt") or self.path.endswith(".docx")

    def as_base64(self):
        with self.as_stream() as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def as_stream(self):
        return state.get_snowpark().get_document(self.path)
