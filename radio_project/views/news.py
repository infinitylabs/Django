from django import forms
from ..models import NewsComments, News
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from captcha.fields import ReCaptchaField
from django.conf import settings

class NewsCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    class Meta:
        model = NewsComments
        fields = ('nickname', 'text', 'mail', 'captcha')

def index(request):
    base_template = "default/barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "default/base.html"
    nid = request.GET.get("nid", None)
    formset = None
    if nid:
        if request.method == "POST":
            formset = NewsCommentForm(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()
        else:
            formset = NewsCommentForm()
            #captcha = ReCaptchaField(public_key=settings.RECAPTCHA_PUBLIC_KEY,
             #                        private_key=settings.RECAPTCHA_PRIVATE_KEY)
            #formset.captcha = captcha
            try:
                news = [News.objects.get(pk=nid)]
                comments = NewsComments.objects.filter(news=nid)
            except News.DoesNotExist:
                news = None
                comments = []
    else:
        news = News.objects.order_by("-time").all()[:10]
        comments = None
    return render_to_response("default/news.html",
                              {"base_template": base_template,
                               "formset": formset,
                               "news": news,
                               "comments": comments},
                              context_instance=RequestContext(request))

def api(request):
    pass