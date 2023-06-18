import streamlit as st
from snowflake.snowpark import FileOperation


class SnowparkConnector:

    def __init__(self, **kwargs):
        self.__stage = kwargs.pop("stage")
        self.__connection = st.experimental_connection('snowpark', **kwargs)

    def get_document(self, doc_name: str):
        with self.__connection.safe_session() as session:
            down_file = FileOperation(session).get_stream(stage_location=f'@{self.__stage}/' + doc_name)
            return down_file

    def get_list_of_file_names(self, limit: int = 20):
        res = self.__connection.query(f'SELECT relative_path FROM directory(@{self.__stage});', ttl=0)
        return res['RELATIVE_PATH'].values.tolist()[:limit]
