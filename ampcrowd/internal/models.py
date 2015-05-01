from basecrowd.abstract_crowd_models import AbstractCrowdTask, AbstractCrowdWorker, AbstractCrowdWorkerResponse, \
    AbstractCrowdTaskGroup

# Inherited crowd models for the interface.
# No need for special subclasses, we use the base implementations.
class CrowdTaskGroup(AbstractCrowdTaskGroup): pass
class CrowdTask(AbstractCrowdTask): pass
class CrowdWorker(AbstractCrowdWorker): pass
class CrowdWorkerResponse(AbstractCrowdWorkerResponse): pass
