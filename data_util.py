from pprint import pprint
from typing import List, Dict

import numpy
from util import data_io


def build_ner_spans(ner:Dict[str,List[List]], is_annotator_of_interest, tok2charoff):
    spans = [
        {
            'start': tok2charoff[token_start],
            'end': tok2charoff[token_end + 0.5],
            'label': label,
            'ann_type': 'T',
            'annotator': annotator

        }
        for annotator, doc_spans in ner.items() if is_annotator_of_interest(annotator)
        for sent_spans in doc_spans
        for token_start, token_end, label in sent_spans]
    [d.update({'id': eid}) for eid, d in enumerate(spans)]
    return spans


def spaced_tokens_and_tokenoffset2charoffset(sentences:List[List[str]]):
    g = [(sent_id,tok) for sent_id,sent in enumerate(sentences) for tok in sent]
    spaced_tokens = [x for tok_id, (sent_id,tok) in enumerate(g) for x in [(tok, tok_id), (' ', tok_id + 0.5)]]
    tok2sent_id = {tok_id:sent_id for tok_id, (sent_id,tok) in enumerate(g)}
    char_offsets = numpy.cumsum([0] + [len(x) for x, _ in spaced_tokens])
    tok2charoff = {tok_id: char_offsets[i] for i, (tok, tok_id) in enumerate(spaced_tokens)}
    return spaced_tokens, tok2charoff,tok2sent_id

def another_span_is_wider(s,spans):
    return any([(s['start']>=o['start']) and (s['end']<=o['end']) and s['id']!=o['id'] for o in spans])

def convert_to_doccano(doc):
    spaced_tokens, tok2charoff,tok2sent_id = spaced_tokens_and_tokenoffset2charoffset(doc['sentences'])
    if not isinstance(doc['ner'],dict):
        ner={'luan':doc['ner']}
    else:
        ner = doc['ner']
    spans = build_ner_spans(ner, lambda x: True, tok2charoff)
    spans = list({'%d-%d'%(s['start'],s['end']):s for s in spans}.values())
    spans = [s for s in spans if not another_span_is_wider(s,spans)]
    assert len(spans)>0
    text = ''.join(s for s,_ in spaced_tokens)
    labels = [[int(s['start']),int(s['end']),s['label']] for s in spans]
    return {'text':text,'labels':labels}


if __name__ == '__main__':
    file = 'data/processed_data/json/train.json'
    data = list(data_io.read_jsonl(file))[:3]
    doccano_datum = convert_to_doccano(data[0])
    pprint(doccano_datum)