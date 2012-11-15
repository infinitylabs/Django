from django import forms
from ..models import NewsComment, News, User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from captcha.fields import ReCaptchaField
from django.conf import settings
from django.forms.fields import CharField
from ..api import Api

class NewsCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    nickname = CharField(initial=u'Anonymous', max_length=100)
    text = CharField(required=True, error_messages={'required':u'You need to enter a comment'}, widget = forms.widgets.Textarea())
    class Meta:
        model = NewsComment
        fields = ('nickname', 'text', 'mail', 'captcha')

def index(request):
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    nid = request.GET.get("nid", None)
    formset = None
    if nid:
        if request.method == "POST":
            formset = NewsCommentForm(request.POST, request.FILES)
            if formset.is_valid():
                #if formset.cleaned_data['nickname'] == u'':
                #    formset.cleaned_data['nickname'] = u'Anonymous' #consistency
                instance = formset.save(commit=False)
                instance.news_id = nid
                if request.user.is_authenticated():
                    instance.poster = request.user
                else:
                    instance.poster = None
                instance.save()
                return render_to_response("<theme>redir.html",
                                          {'redir_time':5,
                                           'redir_url':'/news/?nid=' + nid,
                                           'redir_text': 'Thank you for your comment.'},
                                          context_instance=RequestContext(request))
            return render_to_response("<theme>redir.html",
                                      {'redir_time':5,
                                       'redir_url':'/news/?nid=' + nid,
                                       'redir_text': 'An error occurred when posting the comment.'},
                                      context_instance=RequestContext(request))
        else:
            formset = NewsCommentForm()
            #captcha = ReCaptchaField(public_key=settings.RECAPTCHA_PUBLIC_KEY,
             #                        private_key=settings.RECAPTCHA_PRIVATE_KEY)
            #formset.captcha = captcha
            try:
                news = [News.objects.get(pk=nid)]
                comments = NewsComment.objects.filter(news=nid).order_by('-time')
            except News.DoesNotExist:
                news = None
                comments = []
    else:
        news = News.objects.order_by("-time").all()[:10]
        comments = None
    return render_to_response("<theme>news.html",
                              {"base_template": base_template,
                               "formset": formset,
                               "news": news,
                               "comments": comments},
                              context_instance=RequestContext(request))

@Api(default="jsonp")
def api(request):
    pass