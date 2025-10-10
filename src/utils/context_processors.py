from django.conf import settings
from users.models import LearningProfile

def background_image(request):
    if not request.user.is_authenticated:
        return {}
    
    # check cache
    bg_image = request.session.get('bg_image')
    if bg_image:
        return {"bg_image": bg_image}
    
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    subject_bg = {
        "music": "https://images.unsplash.com/photo-1567787609897-efa3625dd22d?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "art": "https://plus.unsplash.com/premium_photo-1663937576067-14a5dde2f326?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "programming": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1950&q=80",
    }

    bg_image = subject_bg.get(chosen_subject, "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1950&q=80" )

    # save bg image into cache
    request.session["bg_image"] = bg_image
    return {"bg_image": bg_image}
 
