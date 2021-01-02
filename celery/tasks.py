from celery import states
from backend import detect_language
from worker import celery


@celery.task(name='detect.task', bind=True)
def detect(self, text, models):
    self.update_state(state=states.STARTED, meta={})
    results = detect_language(text, models)
    if len(results) == 0:
        self.update_state(state=states.FAILURE)
    return results
