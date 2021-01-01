import string
from typing import Dict, List
import numpy as np
from celery import states
from worker import celery


@celery.task(name='detect.task', bind=True)
def detect(self, text, models):
    self.update_state(state=states.STARTED, meta={})
    text_trigrams = str_2_trigram(text)
    matches_list = list()
    for model in models:
        c = 0
        for tri, freq in text_trigrams.items():
            if tri in model["trigrams"]:
                c += freq
        matches_list.append((c, model))
    # stupid but will work for now
    x = [a[0] for a in matches_list]
    y = [b[1] for b in matches_list]
    x_s = softmax(x)
    results_list = sorted(list(zip(y, x_s)), key=lambda k: k[1], reverse=True)
    results_list = [{"language": z[0]["name"], "iso639_1": z[0]["iso639_1"], "iso639_2": z[0]["iso639_2"], "match": '{0:.2f}%'.format(z[1]*100)} for z in results_list if z[1] > 0.1]
    if len(results_list) == 0:
        self.update_state(state=states.FAILURE)
    return results_list


def str_2_trigram(text: str) -> Dict[str, int]:
    # remove capitalization/punctuation
    fmt_text = ''.join([" " if c in string.punctuation else text.lower() for c in text])
    # add space at start and end
    fmt_text = " {} ".format(fmt_text.strip())
    text_trigrams = dict()
    for i, _ in enumerate(fmt_text):
        if i + 2 >= len(fmt_text):
            break
        tri = fmt_text[i] + fmt_text[i + 1] + fmt_text[i + 2]
        if tri not in text_trigrams:
            text_trigrams[tri] = 0
        text_trigrams[tri] += 1
    return text_trigrams


def softmax(values: List[float], rescale=0.01) -> List[float]:
    values = [x * rescale for x in values]
    e_x = np.exp(values - np.max(values))
    return e_x / e_x.sum()
