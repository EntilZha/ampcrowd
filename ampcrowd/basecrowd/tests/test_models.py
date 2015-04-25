from django.test import TestCase
from basecrowd.models import TaskType, TemplateResource


class TasksTestCase(TestCase):
    def setUp(self):
        html = TemplateResource.objects.create(name="html")
        js = TemplateResource.objects.create(name="js")
        css = TemplateResource.objects.create(name="css")
        bootstrap = TemplateResource.objects.create(name="bootstrap")
        bootstrap.direct_dependencies.add(html, js, css)

        jquery = TemplateResource.objects.create(name="jquery")
        jquery.direct_dependencies.add(html, js, css)

        reactjs = TemplateResource.objects.create(name="reactjs")
        reactjs.direct_dependencies.add(js)

        jqueryui = TemplateResource.objects.create(name="jqueryui")
        jqueryui.direct_dependencies.add(jquery)

        bootstrap_react_gallery = TemplateResource.objects.create(name="bootstrap react gallery")
        bootstrap_react_gallery.direct_dependencies.add(reactjs, bootstrap)

        monolithic_app = TemplateResource.objects.create(name="monolithic app")
        monolithic_app.direct_dependencies.add(
            bootstrap_react_gallery, jqueryui, jquery, js, css, html, reactjs
        )

    def test_template_dependencies(self):
        html = TemplateResource.objects.get(name="html")
        css = TemplateResource.objects.get(name="css")
        js = TemplateResource.objects.get(name="js")
        jquery = TemplateResource.objects.get(name="jquery")
        bootstrap = TemplateResource.objects.get(name="bootstrap")
        reactjs = TemplateResource.objects.get(name="reactjs")
        jqueryui = TemplateResource.objects.get(name="jqueryui")
        bootstrap_react_gallery = TemplateResource.objects.get(name="bootstrap react gallery")
        monolithic_app = TemplateResource.objects.get(name="monolithic app")
        self.assertSetEqual(
            jquery.dependencies,
            {html, css, js}
        )
        self.assertSetEqual(
            html.dependencies,
            set()
        )
        self.assertSetEqual(
            reactjs.dependencies,
            {js}
        )
        self.assertSetEqual(
            jqueryui.dependencies,
            {jquery, html, js, css}
        )
        self.assertSetEqual(
            bootstrap_react_gallery.dependencies,
            {html, js, css, reactjs, bootstrap}
        )
        self.assertSetEqual(
            monolithic_app.dependencies,
            {html, js, css, reactjs, jquery, jqueryui, bootstrap, bootstrap_react_gallery}
        )
