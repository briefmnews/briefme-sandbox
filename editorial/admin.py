from django.contrib import admin, messages

from suit.admin import SortableModelAdminBase, SortableModelAdmin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from typographie.admin import TypographieAdmin

from .models import (
    Issue,
    News,
)
from .forms import NewsForm, IssueForm


class NestedSortableStackedInline(SortableModelAdminBase, NestedStackedInline):
    """To have nested with sortable"""

    pass


class NewsInline(NestedSortableStackedInline):
    model = News
    form = NewsForm
    sortable = "position"
    suit_classes = "suit-tab suit-tab-brief full-width"
    extra = 0
    fields = [
        "title",
        "template",
        "data",
        "image",
    ]
    view_on_site = False


class IssueAdmin(TypographieAdmin, NestedModelAdmin):
    form = IssueForm
    fieldsets = (
        (None, {"fields": ("publication",), "classes": ("suit-tab", "suit-tab-meta")}),
        (None, {"fields": ("title",), "classes": ("suit-tab", "suit-tab-brief")}),
        (
            "Intro",
            {
                "fields": ("intro",),
                "classes": ("suit-tab", "suit-tab-brief", "full-width"),
            },
        ),
        (
            "Outro",
            {
                "fields": ("outro",),
                "classes": ("suit-tab", "suit-tab-brief", "full-width"),
            },
        ),
        (
            "Workflow",
            {
                "fields": (
                    ("status", "template", "published_at"),
                    ("pushed", "pushed_at", "i_am_sure"),
                ),
                "classes": ("suit-tab", "suit-tab-meta"),
            },
        ),
        (
            "Preview",
            {
                "fields": ("email_content_iframe",),
                "classes": ("suit-tab", "suit-tab-preview"),
            },
        ),
    )
    suit_form_tabs = (("brief", "Brief"), ("meta", "Meta"), ("preview", "Preview"))

    list_display = ("__str__", "created", "status", "pushed")
    readonly_fields = ("pushed", "pushed_at", "email_content_iframe", "template")
    inlines = (NewsInline,)
    search_fields = ["title"]

    class Media:
        js = ("editorial/js/editorial.js",)
        css = {"all": ("editorial/css/editorial.css",)}


class NewsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "issue", "created")
    search_fields = ("title", "issue__title")


admin.site.register(Issue, IssueAdmin)
admin.site.register(News, NewsAdmin)
