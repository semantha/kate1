import os

import streamlit as st

from pages_views.abstract_pages import AbstractContentPage


class HowToPage(AbstractContentPage):
    def __init__(self, page_id: int):
        super().__init__()
        if page_id == 1:
            self._content_placeholder = st.container()
        else:
            self._content_placeholder = st.empty()

    def _display_content(self):
        st.write("In general, K-A-T-E One can be used in conjunction with Snowflake to help users view, search for, and list data in real time. This can be particularly useful for businesses that need to quickly access and analyze large amounts of unstructured data in order to make informed decisions. With K-A-T-E One, users can easily locate and extract the data they need from Snowflake, saving them time and improving their overall efficiency.")

        st.header("How to use K-A-T-E One")
        st.write('K-A-T-E One is an artificial intelligence service for document analysis. This service is specifically designed to help individuals and organizations conduct an in-depth analysis of their documents.')
        st.write('One of the key features of K-A-T-E One is its ability to analyze documents related to Environmental, Social, and Governance (ESG) issues. This is done using a library of guidelines and regulations to ensure that analyzed documents are thoroughly examined according to relevant standards. With K-A-T-E One, users can gain valuable insights into their ESG-related documents, which can inform decision-making and help organizations stay in compliance with regulations.')

        st.subheader("Individual Document")
        st.write('To start an analysis using K-A-T-E One, you can upload your own document and click the "Analyze" button. Alternatively,  you can use the provided sample document by just clicking the "Analyze" button.')
        st.write('You can adjust the strictness of the comparison, which determines how closely content should be interpreted, in the left sidebar. You may need to expand the sidebar by clicking the arrow.')
        st.write('Once the analysis is initiated, K-A-T-E One processes the document and generates results in just a few seconds. The result dashboard shows the analysis results in the form of bar charts, along with corresponding labels for each page.')
        st.write('The text-to-text matches indicate the degree of similarity between the document and the library of guidelines and regulations. This feature enables you to quickly identify potential inconsistencies or discrepancies that may require further attention.')
        st.write('In addition, there is an interactive sunburst chart available. You can use it to see a more dynamic visual representation of the data.')
        st.write('In the sidebar on the left, you can also apply filters to customize and refine the displayed results to suit your specific needs.')

        st.subheader("Document Collection")
        st.write('This showcase contains a collection of sample documents sourced from various locations in Snowflake. The objective is to examine the collected policies based on the library containing ESG guidelines and regulations.')
        st.write('To start the analysis of the Document Collection, click the "Analyze Document Collection" button.')
        st.write('You can adjust the strictness of the comparison, which determines how closely content should be interpreted, in the left sidebar. You may need to expand the sidebar by clicking the arrow.')
        st.write('For each of the documents in the collection, the covered ESG topics are highlighted')
        st.write('You can select a topic to obtain a summary of the corresponding findings.')
        st.write('Furthermore, a detailed view of the analyzed document, as described in "Individual Document" above, can also be displayed.')
        st.write('This showcase aims to provide a comprehensive overview of ESG policies and their compliance status in the presented sample documents.')

        with st.expander(label="How To Video", expanded=False):
            st.image(os.path.join(os.path.dirname(__file__), "..", "images", "how_to_v3.gif"), output_format="GIF", use_column_width=True)
