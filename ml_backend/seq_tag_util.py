import numpy as np
from sklearn import metrics


def bilou2bio(tag_seq):
    '''
    BILOU to BIO
    or
    BIOES to BIO
    E == L
    S == U
    '''
    bio_tags = tag_seq
    for i in range(len(tag_seq)):
        if tag_seq[i].startswith('U-') or tag_seq[i].startswith('S-'):
            bio_tags[i] = 'B-'+tag_seq[i][2:]
        elif tag_seq[i].startswith('L-') or tag_seq[i].startswith('E-'):
            bio_tags[i] = 'I-'+tag_seq[i][2:]
    return bio_tags


def spanwise_pr_re_f1(label_pred, label_correct):
    pred_counts = [compute_TP_P(pred, gold) for pred,gold in zip(label_pred,label_correct)]
    gold_counts = [compute_TP_P(gold, pred) for pred,gold in zip(label_pred,label_correct)]
    prec = np.sum([x[0] for x in pred_counts]) / np.sum([x[1] for x in pred_counts])
    rec = np.sum([x[0] for x in gold_counts]) / np.sum([x[1] for x in gold_counts])
    f1 = 0
    if (rec + prec) > 0:
        f1 = 2.0 * prec * rec / (prec + rec)
    return prec, rec, f1


def calc_seqtag_tokenwise_scores(gold_seqs, pred_seqs):
    gold_flattened = [l for seq in gold_seqs for l in seq]
    pred_flattened = [l for seq in pred_seqs for l in seq]
    assert len(gold_flattened) == len(pred_flattened) and len(gold_flattened)>0
    labels = list(set(gold_flattened))
    scores = {
        'f1-micro': metrics.f1_score(gold_flattened, pred_flattened, average='micro'),
        'f1-macro': metrics.f1_score(gold_flattened, pred_flattened, average='macro'),
        'clf-report': metrics.classification_report(gold_flattened, pred_flattened, target_names=labels, digits=3,
                                                    output_dict=True),
    }
    return scores


def compute_TP_P(guessed, correct):
    assert len(guessed) == len(correct)
    correctCount = 0
    count = 0

    idx = 0
    while idx < len(guessed):
        if guessed[idx][0] == 'B':  # A new chunk starts
            count += 1

            if guessed[idx] == correct[idx]:
                idx += 1
                correctlyFound = True

                while idx < len(guessed) and guessed[idx][0] == 'I':  # Scan until it no longer starts with I
                    if guessed[idx] != correct[idx]:
                        correctlyFound = False

                    idx += 1

                if idx < len(guessed):
                    if correct[idx][0] == 'I':  # The chunk in correct was longer
                        correctlyFound = False

                if correctlyFound:
                    correctCount += 1
            else:
                idx += 1
        else:
            idx += 1

    return correctCount,count