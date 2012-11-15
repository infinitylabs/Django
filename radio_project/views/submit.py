from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.fields import FileField
from ..models import Collection, Song, Radvar, Upload, Track, Album, Listener, TrackHasAlbum
from ..tools import get_filename
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from datetime import datetime, timedelta

submitmessage = """<p>You can only upload one song every hour. The song also has to be reviewed before you can request it; this can take a few days or more.</p>
            <p>If you supply the source (anime, VN, whatever) in the comment, it will speed things up dramatically for us.</p>
            <p>Keep in mind that the maximum file size is 15MB; anything over that will be automatically rejected.</p>
            <p><b>Please make sure to check the existing database for your song before uploading it.<br />
            Also please make sure to mention the artist when you are uploading a cover, we are having a hard time finding out the artist without.</b></p>
            <p>Don't know how to tag MP3 files? <a href="/submit/tagging.html" target="_blank">Here's a guide!</a></p>"""

def check_daypass(daypass):
    try:
        return Radvar.objects.get(name="daypass") == daypass
    except:
        return False

class MultiChoice(forms.ModelChoiceField):
    def __init__(self):
        super(MultiChoice, self).__init__(required=False, queryset=Collection.objects.filter(status=Collection.REPLACEMENT))
        
    def label_from_instance(self, obj):
        return obj.songs.track.metadata
    
class SubmitForm(forms.Form):
    track = forms.FileField()
    comment = forms.CharField(max_length=100, required=False)
    daypass = forms.CharField(max_length=100, required=False)
    replace = MultiChoice()
    
def index(request):
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    formset = None
    uploadmessage = False
    canupload = True
    client_ip = request.META.get("REMOTE_ADDR", None)
    if not client_ip:
        uploadmessage = u"You don't have an IP address?"
    else:
        time_threshold = datetime.now() - timedelta(hours=1)
        recent_uploads = [upload.collection.songs.track.metadata for upload in Upload.objects.filter(listeners__ip=client_ip,
                               time__gt=time_threshold)]
        if recent_uploads:
            # You already uploaded something!
            uploadmessage = u"You can't upload another song this quickly. Because you've recently uploaded <b>{uploads}</b>.".format(uploads=" ,".join(recent_uploads))
        if not uploadmessage or \
                request.user.is_authenticated():
            canupload = True
    if request.method == "POST":
        formset = SubmitForm(request.POST, request.FILES)
        if formset.is_valid():
            if canupload or check_daypass(formset.cleaned_data["daypass"]):
                file = formset.files['track']
                try:
                    filename = file.temporary_file_path()
                except AttributeError:
                    uploadmessage = u"Please poke someone on IRC about error code 5000."
                else:
                    # Get our info from mutagen
                    mediafile = mutagen.File(filename, easy=True)
                    if isinstance(mediafile, FLAC):
                        if file.size > 7.34e+7:
                            uploadmessage = u"Uploaded file too large."
                    elif isinstance(mediafile, (MP3, OggVorbis)):
                        if file.size > 15728640:
                            uploadmessage = u"Uploaded file too large."
                    else:
                        # Fuck off, we don't want your kind here!
                        uploadmessage = u"Uploaded file was of unsupported format."
                
                    # Are we still okay?
                    if not uploadmessage:
                        # Wow you actually got all the way here!
                        # Merge artist and track
                        album = " ,".join(mediafile.get('album', u''))
                        artist = " ,".join(mediafile.get('artist', u''))
                        title = " ,".join(mediafile.get('title', u''))
                        if artist:
                            metadata = artist + u" - " + title
                        else:
                            metadata = title
                        # Create or get our track object
                        track, created = Track.objects.get_or_create(metadata=metadata,
                                      defaults={'length': int(mediafile.info.length)})
                        if not created:
                            track.save()
                        else:
                            track.length = int(mediafile.info.length)
                            track.save()
                        
                        # Handle album entry
                        if album:
                            album, created = Album.objects.get_or_create(name=album)
                            if not created:
                                album.save()
                            TrackHasAlbum(track=track, album=album).save()
                            
                            
                        # Get our song object
                        songs, created = Song.objects.get_or_create(hash=track.hash,
                                                           track=track)
                        if not created:
                            songs.save()
                        
                        final_filename = get_filename(file)
                        
                        collection, created = Collection.objects.get_or_create(songs=songs,
                                    defaults={'usable': 0,
                                              'filename': final_filename,
                                              'good_upload': 0,
                                              'need_reupload': 0,
                                              'popularity': 0,
                                              'status': Collection.PENDING,
                                              'comment': formset.cleaned_data['comment'],
                                              'original_filename': file.name})
                        # 
                        listener, created = Listener.objects.get_or_create(ip=client_ip,
                                    defaults={'last_seen': datetime.now(),
                                              'banned': 0})
                        if not created:
                            listener.last_seen = datetime.now()
                        listener.save()
                            
                        upload_entry = Upload(listeners=listener,
                                               collection=collection,
                                               time=datetime.now())
                        upload_entry.save()
                        
                        with open(final_filename, "wb+") as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)
                        uploadmessage = u"Thank you for your upload."
        else:
            uploadmessage = u"How about actually uploading a file?"
    else:
        formset = SubmitForm()
    declined = Collection.objects.filter(status=Collection.DECLINED,
                                         collectioneditors__action="decline").order_by("-collectioneditors__time")[:50]
    accepted = Collection.objects.filter(status=Collection.ACCEPTED,
                                         collectioneditors__action="accept").order_by("-collectioneditors__time")[:50]
    if not uploadmessage:
        uploadmessage = u"Welcome to the submit page, read the instructions below."
    return render_to_response("<theme>submit.html",
                              {"base_template": base_template,
                               "formset": formset,
                               "declined": declined,
                               "accepted": accepted,
                               "submitmessage": submitmessage,
                               "uploadmessage": uploadmessage,
                               "canupload": canupload},
                              context_instance=RequestContext(request))