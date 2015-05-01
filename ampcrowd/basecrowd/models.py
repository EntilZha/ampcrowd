from django.db import models
from django.db.models.signals import class_prepared
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


# Model for a group of tasks
class AbstractCrowdTaskGroup(models.Model):

    # The group id
    group_id = models.CharField(primary_key=True, max_length=64)

    # The number of HITs in this group that have been finished
    tasks_finished = models.IntegerField()

    # The call back URL for sending results once complete
    callback_url = models.URLField()

    # Context for rendering the tasks to the crowd, as a JSON blob.
    group_context = models.TextField()

    # The configuration specific to current crowd type
    crowd_config = models.TextField()

    def __unicode__(self):
        return self.group_id

    class Meta:
        abstract = True

    @staticmethod
    def to_json(task_group):
        return {
            'group_id': task_group.group_id,
            'tasks_finished': task_group.tasks_finished,
        }


# Model for an individual task.
class AbstractCrowdTask(models.Model):

    # The group that this task belongs to, a many-to-one relationship.
    # The relationship will be auto-generated to the task_group class of the
    # registered crowd, and can be accessed via the 'group' attribute.
    # The related_name will be 'tasks' to enable reverse lookups, e.g.
    # group = models.ForeignKey(CrowdTaskGroup, related_name='tasks')

    # The type of the task, Sentiment Analysis, Deduplication, etc
    task_type = models.CharField(max_length=64)

    # The data for the task, specific to the task type (stored as a JSON blob)
    data = models.TextField()

    # Creation time
    create_time = models.DateTimeField()

    # Unique identifier for the task
    task_id = models.CharField(primary_key=True, max_length=64)

    # The number of assignments (i.e., number of votes) to get for this task.
    num_assignments = models.IntegerField()

    # Answer based on majority vote
    mv_answer = models.TextField()

    # Answer based on Expectation Maximization
    em_answer = models.TextField()

    # Has the task received enough responses?
    is_complete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.task_type + " : " + self.data

    class Meta:
        abstract = True

    @staticmethod
    def to_dict(task):
        return {
            'task_type': task.task_type,
            'data': task.data,
            'creation_time': task.create_time,
            'task_id': task.task_id,
            'num_assignments': task.num_assignments,
            'mv_answer': task.mv_answer,
            'em_answer': task.em_answer,
            'is_complete': task.is_complete,
            'completed_assignments': len(task.responses.all())
        }


# Model for workers
class AbstractCrowdWorker(models.Model):

    # The tasks a worker has been assigned, a many-to-many relationship.
    # The relationship will be auto-generated to the task class of the
    # registered crowd, and can be accessed via the 'tasks' attribute.
    # The related_name will be 'workers' to enable reverse lookups, e.g.
    # tasks = models.ManyToManyField(CrowdTask, related_name='workers')

    # A unique id for the worker
    worker_id = models.CharField(primary_key=True, max_length=64)

    def __unicode__(self):
        return self.worker_id

    class Meta:
        abstract = True


# Model for a worker's response to a task
class AbstractCrowdWorkerResponse(models.Model):

    # The task that was responded to, a many-to-one relationship.
    # The relationship will be auto-generated to the task class of the
    # registered crowd, and can be accessed via the 'task' attribute.
    # The related_name will be 'responses' to enable reverse lookups, e.g.
    # task = models.ForeignKey(CrowdTask, related_name='responses')

    # The worker that gave the responded, a many-to-one relationship.
    # The relationship will be auto-generated to the worker class of the
    # registered crowd, and can be accessed via the 'worker' attribute.
    # The related_name will be 'responses' to enable reverse lookups, e.g.
    # worker = models.ForeignKey(CrowdWorker, related_name='responses')

    # The content of the response (specific to the task type).
    content = models.TextField()

    # The assignment id of this response
    assignment_id = models.CharField(max_length=200)

    def __unicode__(self):
        return self.task.task_id + " " + self.worker.worker_id

    class Meta:
        abstract = True


# Register a set of models as a new crowd.
class CrowdModelSpecification(object):
    def __init__(self, crowd_name,
                 task_model,
                 group_model,
                 worker_model,
                 response_model):
        self.name = crowd_name
        self.task_model = task_model
        self.group_model = group_model
        self.worker_model = worker_model
        self.response_model = response_model

    @staticmethod
    def add_rel(from_cls, to_cls, relation_cls, relation_name, related_name=None):
        field = relation_cls(to_cls, related_name=related_name)
        field.contribute_to_class(from_cls, relation_name)

    def add_model_rels(self):
        # tasks belong to groups
        self.add_rel(self.task_model, self.group_model, models.ForeignKey,
                     'group', 'tasks')

        # workers work on many tasks, each task might have multiple workers
        self.add_rel(self.worker_model, self.task_model, models.ManyToManyField,
                     'tasks', 'workers')

        # responses come from a worker
        self.add_rel(self.response_model, self.worker_model, models.ForeignKey,
                     'worker', 'responses')

        # responses pertain to a task
        self.add_rel(self.response_model, self.task_model, models.ForeignKey,
                     'task', 'responses')


class TemplateResource(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    direct_dependencies = models.ManyToManyField('self', symmetrical=False, related_name="upstream_dependencies")
    direct_requirements = models.ManyToManyField('self', symmetrical=False, related_name="upstream_requirements")

    @property
    def dependencies(self):
        query_set = list(self.direct_dependencies.all())
        all_dependencies = set(query_set)
        current_dependencies = list(query_set)
        while True:
            prior_size = len(all_dependencies)
            new_dependencies = set()
            for dep in current_dependencies:
                deps = set(dep.direct_dependencies.all())
                new_dependencies = new_dependencies.union(deps)
                all_dependencies = all_dependencies.union(deps)
            if prior_size == len(all_dependencies):
                break
            else:
                current_dependencies = list(new_dependencies)
        return all_dependencies

    @property
    def requirements(self):
        pass


    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=200)
    iterator_template = models.ForeignKey(TemplateResource, related_name='iterator_task')
    point_template = models.ForeignKey(TemplateResource, related_name='point_task')
    renderer = models.ForeignKey(TemplateResource, related_name='renderer_task')
