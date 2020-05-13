import uuid

from django.conf import settings
from django.db import models

from autoslug import AutoSlugField
from django_reactive.fields import ReactJSONSchemaField, TemplateField
from model_utils.models import TimeStampedModel

from briefme_editorial import models as base_models

from .utils import (
    apply_func_to_dict,
    add_target_blank_to_links,
)
from .schemas import schemas


class AddLinkTargetBlankMixin:
    """To parse the content and a target blank on all links"""

    def save(self, *args, **kwargs):
        """Modify all links to add a target blank"""
        self.data = apply_func_to_dict(
            self.data, self.get_html_data_fields(), add_target_blank_to_links
        )
        super(AddLinkTargetBlankMixin, self).save(*args, **kwargs)


class Publication(base_models.Publication):
    slug = models.SlugField(max_length=30, unique=True)
    can_push = models.BooleanField(default=False)


class Issue(base_models.Issue):
    slug = AutoSlugField(
        null=True, default=None, unique=False, populate_from="title", max_length=200
    )
    publication = models.ForeignKey(
        Publication, default=settings.DEFAULT_PUBLICATION, on_delete=models.CASCADE
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta(base_models.Issue.Meta):
        ordering = ["-published_at"]


class Section(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=16)
    color = models.CharField(max_length=7)
    order = models.PositiveIntegerField()
    publication = models.ForeignKey(Publication, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class News(AddLinkTargetBlankMixin, base_models.News):
    TEMPLATES = [
        ("basic", "Basique", schemas["basic"]),
        ("image", "Image", schemas["image"]),
        ("quote", "Citation", schemas["quote"]),
        ("questions", "Questions", schemas["questions"]),
        ("rewind", "On rembobine", schemas["rewind"]),
        ("start", "On revient au début", schemas["start"]),
    ]

    utitle = models.CharField(max_length=200, blank=True)
    slug = AutoSlugField(
        null=True, default=None, unique=False, populate_from="get_slug", max_length=200
    )
    template = TemplateField(templates=TEMPLATES, max_length=200, default="basic")
    data = ReactJSONSchemaField(template="template", blank=True)
    image = models.ImageField(blank=True)
    image_sn = models.ImageField(blank=True)
    issue = models.ForeignKey(Issue, related_name="news", on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta(base_models.News.Meta):
        ordering = ["position"]
