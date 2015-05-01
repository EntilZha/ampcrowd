from django.db import models


class TemplateResource(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    direct_imports = models.ManyToManyField('self', symmetrical=False, related_name="downstream_imports")
    direct_requirements = models.ManyToManyField('self', symmetrical=False, related_name="downstream_requirements")

    @property
    def imports(self):
        query_set = list(self.direct_imports.all())
        all_imports = set(query_set)
        current_imports = list(query_set)
        while True:
            prior_size = len(all_imports)
            new_imports = set()
            for dep in current_imports:
                deps = set(dep.direct_imports.all())
                new_imports = new_imports.union(deps)
                all_imports = all_imports.union(deps)
            if prior_size == len(all_imports):
                break
            else:
                current_imports = list(new_imports)
        return all_imports

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
