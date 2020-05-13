import re

from django import forms

from .models import News, Issue


def format_source(text):
    """
    Add a span around [] that start with an a
    Input: [<a href="http://example.com">Some link | </a>]
    Output: <span class="source">[<a href="http://example.com">Some link | </a>]</span>  # noqa
    """
    return re.sub(
        r'(?<!<span class="source">)(\[<a.*?\])',
        r'<span class="source">\1</span>',
        text,
    )


class NewsForm(forms.ModelForm):
    class Meta:
        exclude = ()
        model = News


class IssueForm(forms.ModelForm):
    i_am_sure = forms.BooleanField(
        label="Forcer la publication", required=False, widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)

        if self.errors.get("i_am_sure"):
            # show the 'are you sure' checkbox when we want confirmation
            self.fields["i_am_sure"].widget = forms.CheckboxInput()

    def clean(self):
        cleaned_data = super(IssueForm, self).clean()

        if not self.errors:
            # only validate i_am_sure once all other validation has passed
            # if there is a transition to published from another state
            # and it has not been pushed yet
            if (
                cleaned_data["status"] == Issue.STATUS.published
                and self.instance.status != cleaned_data["status"]
                and self.instance.pushed is False
            ):
                i_am_sure = cleaned_data.get("i_am_sure")
                if self.instance.id and not i_am_sure:
                    self._errors["i_am_sure"] = self.error_class(
                        [
                            "Are you sure you want to publish this issue "
                            "and push a notifcation?"
                        ]
                    )
                    del cleaned_data["i_am_sure"]

        return cleaned_data

    class Meta:
        exclude = ()
        model = Issue
        widgets = {"title": forms.TextInput(attrs={"cols": 60})}
