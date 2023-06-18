import logging
import os

import altair
import pandas as pd
import plotly.express as px
import streamlit as st
from semantha_sdk.model.document import Document
from semantha_sdk.model.document_class import DocumentClass

import state
from pages_views.abstract_pages import AbstractContentPage
from util.semantha_model_handling import get_paragraph_matches_of_doc
from util.text_handling import short_text


class ComparePage(AbstractContentPage):
    __MATCH_COLUMN_DEF = [5.9, 1.1, 5.9]
    __LIB_MATCH_COLUMN_DEF = [1.0, 0.2, 5.0]
    __EXAMPLE_FILE = "Statutory-Sustainability-Report-Fiscal-Year-2021.pdf"

    def __init__(self, page_id: int):
        super().__init__()
        if page_id == 2:
            self._content_placeholder = st.container()
        else:
            self._content_placeholder = st.empty()
        self.__upload_disabled = True

    def _display_content(self):
        st.write(f"By default, a sample sustainability report is used for the comparison ({self.__EXAMPLE_FILE}). "
                 "If you want to use your own document, please upload it below.")

        __selected_file_name = self.__EXAMPLE_FILE

        with st.expander(label="Upload your own document or directly click 'Analyze' to use the provided sample document.", expanded=False):
            __cmp_input_up = st.file_uploader("upload", key='cmp_input_up', label_visibility="collapsed")
            if __cmp_input_up is not None:
                __selected_file_name = __cmp_input_up.name

        __file_select, __col2, _ = st.columns([2, 1, 2])
        __comp_button = __col2.button('Analyze', disabled=False, key='cmp_docs')

        if __comp_button:
            with st.spinner("Comparing document to references..."):
                logging.info("Comparing document to references...")
                if __cmp_input_up is None:
                    logging.info(f"No document uploaded. Using example document: '{self.__EXAMPLE_FILE}'")
                    __cmp_input_up = self.__open_example_file(self.__EXAMPLE_FILE)
                else:
                    logging.info(f"Document uploaded. Using uploaded document: '{__cmp_input_up.name}'")
                state.set_single_document_with_references(
                    __selected_file_name,
                    state.get_semantha().compare_to_library(
                        in_file=__cmp_input_up,
                        threshold=state.get_similarity_threshold()
                    )
                )
                st.success(
                    f"Done! The analysis results are shown below..."
                )
                logging.info("... done (comparing document to references)")
        with __file_select.container():
            st.info(f"Selected File: __{__selected_file_name}__")
        __doc_tuple = state.get_single_document_with_references()
        __doc = __doc_tuple[1]
        if __doc is not None:
            st.divider()
            st.subheader(f"Results for file '{__doc_tuple[0]}'")
            __selected_tags = state.get_selected_tags_compare_view()
            self.__display_overall_stats(__doc)
            self.__display_matches_per_tags_per_page(__doc, __selected_tags)
            self.__display_library_matches_per_tag(__doc)
            self.__display_sunburst_chart(__doc, __selected_tags)
            self.__display_matches(__doc, __selected_tags, __doc.id)

    def __display_overall_stats(self, doc):
        __paragraph_matches = get_paragraph_matches_of_doc(doc)

        with st.expander(label="Statistics", expanded=True):
            st.subheader(f"Total Matches: {len(__paragraph_matches)}")

    def __display_matches_per_tags_per_page(self, doc, __selected_tags):
        with st.expander(label="Visualization of Matches by Topics per Page", expanded=True):
            st.subheader(f"Matches by Topics per Page")
            chart_data = self.__calculate_matches_per_page(doc, __selected_tags, doc.id)
            if len(chart_data) == 0:
                st.error("Nothing to display. Please adjust the filter(s) or start a new analysis.")
            else:
                chart = altair.Chart(chart_data).mark_bar().encode(
                    x=altair.X('Page', axis=altair.Axis(labelAngle=0), sort=None),
                    y=altair.Y('sum(References)', title='Number of Matches'),
                    color='Topic',
                    tooltip='Topic'
                )
                st.altair_chart(chart, use_container_width=True)

    @st.cache_data(show_spinner="Fetching matches ...")
    def __display_matches(_self, _doc, selected_tags, doc_id):

        logging.info(f"Fetching matches for document {doc_id} with selected tags: {selected_tags}")
        with st.expander(label="Text-to-Text Matches", expanded=True):
            st.subheader('Matching Sections')
            __matches = get_paragraph_matches_of_doc(_doc)
            if len(__matches) == 0:
                st.error(f"Found no matches for selected topics: {selected_tags}")
            for idx, match in enumerate(__matches):
                ref_0 = match[1][0]
                ref_0_tags = state.get_semantha().get_tags_of_library_document(ref_0.document_id)
                if ref_0_tags is None:
                    ref_0_tags = []
                if len(ref_0_tags) == 0:
                    ref_0_tags.append(state.NO_TAG)
                hit = False
                if len(selected_tags) == 0:
                    hit = True
                else:
                    for ref_0_tag in ref_0_tags:
                        if ref_0_tag in selected_tags:
                            hit = True
                            continue
                if hit:
                    with st.container():
                        st.caption(f"_Match {idx + 1}: {', '.join(ref_0_tags)}_")
                        col_input_text, col_sim_text, col_reference_text = st.columns(_self.__MATCH_COLUMN_DEF)
                        if ref_0.similarity > state.CONST_HIGH_SIM:
                            color = state.CONST_HIGH_SIM_COLOR
                        elif ref_0.similarity > state.CONST_MID_SIM:
                            color = state.CONST_MID_SIM_COLOR
                        else:
                            color = state.CONST_LOW_SIM_COLOR
                        text_ref_0 = state.get_semantha().get_text_of_library_paragraph(ref_0.document_id,
                                                                                        ref_0.paragraph_id)
                        col_input_text.markdown(f'<p style=text-align:justify>{match[0].text}</p>',
                                                unsafe_allow_html=True)
                        col_sim_text.markdown(
                            f'<p style="background-color:{color};text-align:center">⇄ | {(ref_0.similarity * 100):2.2f} %</p>',
                            unsafe_allow_html=True)
                        col_reference_text.markdown(f'<p style=text-align:justify>{text_ref_0}</p>',
                                                    unsafe_allow_html=True)
                        st.divider()

    def __display_sunburst_chart(self, doc, __selected_tags):
        __paragraph_matches = get_paragraph_matches_of_doc(doc)
        with st.expander(label="Visualization of Matches per Topic", expanded=True):
            st.subheader(f"Distribution of Matches per Topic")
            __labels, __parents = self.__retrieve_categories_for_sunburst_chart(__selected_tags, __paragraph_matches, doc.id)
            data = dict(
                character=[short_text(label) for label in __labels],
                parent=[short_text(parent) for parent in __parents],
                hover=__labels
            )
            fig = px.sunburst(data, names='character', parents='parent', hover_name='hover', hover_data={"character": False, "parent": False, "hover": False}, height=1200, width=8000)
            st.plotly_chart(fig, use_container_width=True)

    def __display_library_matches_per_tag(self, doc):
        __available_tags = state.get_semantha().get_library_tags()
        __tag_match_dict = self.__retrieve_library_matches_per_tag(__available_tags, doc, doc.id)
        __selected_tag = __available_tags[0]
        with st.expander(label="Library Matches per Topic", expanded=True):
            col_h1, _, col_h2 = st.columns(self.__LIB_MATCH_COLUMN_DEF)
            col_tags, _, col_matches = st.columns(self.__LIB_MATCH_COLUMN_DEF)
            with col_h1.container():
                st.subheader("Available Topics")
            with col_tags.container():
                for __tag in __available_tags:
                    col_marker, col_button = st.columns([1, 15])
                    if len(__tag_match_dict[__tag]["matched"]) > 0:
                        col_marker.markdown('✔')
                    else:
                        col_marker.markdown('✖️')
                    __tag_button = col_button.button(__tag, disabled=False, key=f'tag_button_{__tag}', use_container_width=True)
                    if __tag_button:
                        __selected_tag = __tag
            with col_h2.container():
                st.subheader(f"For topic '{__selected_tag}' matches were found for the following library items")
            with col_matches.container():
                __matched = __tag_match_dict[__selected_tag]["matched"]
                __not_matched = __tag_match_dict[__selected_tag]["not_matched"]
                for m in __matched:
                    st.success(f"__{m.name.strip()}__: '{m.content_preview}'")
                st.subheader(f"For topic '{__selected_tag}' _no_ matches were found for the following library items")
                for nm in __not_matched:
                    st.error(f"__{nm.name.strip()}__: '{nm.content_preview}'")

    @st.cache_data(show_spinner="Retrieving library matches per topic...")
    def __retrieve_library_matches_per_tag(_self, tags, _doc, doc_id):
        logging.info(f"Retrieving library matches per tag for tags {tags} and document with id {doc_id}")
        result_dict = {}
        for t in tags:
            __matched = []
            __not_matched = []
            __doc_ids_of_paragraph_matches = [i.document_id for x in get_paragraph_matches_of_doc(_doc) for i in x[1]]
            __lib_entries_for_tag = state.get_semantha().get_library_entries_for_tag(t)
            for entry in __lib_entries_for_tag:
                if entry.id in __doc_ids_of_paragraph_matches:
                    __matched.append(entry)
                else:
                    __not_matched.append(entry)
            result_dict[t] = {
                "matched": __matched,
                "not_matched": __not_matched
            }
        return result_dict

    @staticmethod
    def __open_example_file(file_name: str):
        return open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "single", file_name), "rb")

    @st.cache_data(show_spinner="Fetching matches per page...")
    def __calculate_matches_per_page(_self, _doc: Document, selected_tags, doc_id):

        logging.info(f"Fetching matches for document {doc_id} with selected tags: {selected_tags}")

        __matches_dict = {}
        __ref_tag_cache = {}
        for idx, p in enumerate(_doc.pages):
            if str(idx) not in __matches_dict:
                __matches_dict[str(idx)] = {}
            if p.contents is not None:
                for c in p.contents:
                    if c.paragraphs is not None:
                        for par in c.paragraphs:
                            if par.references is not None:
                                for ref in par.references:
                                    if ref.document_id in __ref_tag_cache:
                                        tags = __ref_tag_cache[ref.document_id]
                                    else:
                                        tags = state.get_semantha().get_tags_of_library_document(ref.document_id)
                                        __ref_tag_cache[ref.document_id] = tags
                                    if len(tags) == 0:
                                        if state.NO_TAG in __matches_dict[str(idx)]:
                                            __matches_dict[str(idx)][state.NO_TAG] += 1
                                        else:
                                            __matches_dict[str(idx)][state.NO_TAG] = 1
                                    for tag in tags:
                                        if tag in __matches_dict[str(idx)]:
                                            __matches_dict[str(idx)][tag] += 1
                                        else:
                                            __matches_dict[str(idx)][tag] = 1
        __matches_rec = []
        for page, tags in __matches_dict.items():
            for tag, count in tags.items():
                if tag in selected_tags or len(selected_tags) == 0:
                    __matches_rec.append([str(int(page) + 1), tag, int(count)])
        __match_df = pd.DataFrame.from_records(
            __matches_rec,
            columns=["Page", "Topic", "References"]
        )
        return __match_df

    @st.cache_data(show_spinner="Fetching topics for sunburst chart...")
    def __retrieve_categories_for_sunburst_chart(_self, selected_tags, __paragraph_matches, doc_id):
        logging.info(f"Fetching categories for sunburst chart for document {doc_id}")
        __characters = []
        __parents = []

        for idx, m in enumerate(__paragraph_matches):
            __ref_0 = m[1][0]
            __matches_tags = state.get_semantha().get_tags_of_library_document(__ref_0.document_id)
            for t in __matches_tags:
                if t in selected_tags or len(selected_tags) == 0:
                    __category = state.get_semantha().get_category_of_document(__ref_0.document_id)
                    if __category is None:
                        if "uncategorized" not in __characters:
                            __characters.append("uncategorized")
                            __parents.append("")
                        __parents.append("uncategorized")
                    else:
                        _self.__add_category(__category, __characters, __parents)
                        __parents.append(__category.name)
                    __characters.append(f"Match {idx + 1}: {short_text(m[0].text, 100)}")
                    continue
        return __characters, __parents

    def __add_category(self, category: DocumentClass, characters, parents):
        __category = state.get_semantha().get_category_by_id(category.id)
        __c_name = __category.name
        if __category.parent_id is None:
            if __c_name not in characters:
                characters.append(__c_name)
                parents.append("")
            return
        else:
            self.__add_category(state.get_semantha().get_category_by_id(__category.parent_id), characters, parents)
            if __c_name not in characters:
                characters.append(__c_name)
                parents.append(state.get_semantha().get_category_by_id(__category.parent_id).name)
