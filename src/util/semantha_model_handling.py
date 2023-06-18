from typing import Tuple, List

from semantha_sdk.model.document import Document
from semantha_sdk.model.paragraph import Paragraph
from semantha_sdk.model.reference import Reference


def get_paragraph_matches_of_doc(doc: Document) -> List[Tuple[Paragraph, List[Reference]]]:
    __match_list = []
    for page in doc.pages:
        if page.contents is not None:
            for content in page.contents:
                if content.paragraphs is not None:
                    for p in content.paragraphs:
                        if p.references is not None and len(p.references) > 0:
                            __match_list.append((p, p.references))

    return __match_list
