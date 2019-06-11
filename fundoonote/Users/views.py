
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.http import JsonResponse # import JsonResponse to use the display the all users in Json Format
from django.contrib.auth.models import User

from rest_framework.generics import CreateAPIView
from rest_framework import viewsets # viewSet is collection of Users
from rest_framework.response import Response # import the Rest_framework implementation
from .tokens import account_activation_token # activate the users account
from .serializers import UserSerializer # import the user serializer to serialize the User data
from .redis import redis_methods  # import the redis_method class from redis file
from .forms import UserForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NotesForm , LabelsForm

from .models import Notes , Labels
try:
    import jwt
except ImportError:
    print("import jwt")

r = redis_methods()
"""this method is used to display the home page"""
def home(request):
    return render(request, 'loginapp/home.html', {})


"""this method is used to enter the Users"""

def enter(request):
      return render(request, 'Users/base.html', {})


"""only after login of user this method can be called"""
def user_logout(request):  # this method is used to logout
    logout(request)
    return HttpResponseRedirect(reverse('home')) # after logout user reverse the index



"""this method is used to signup the user"""
def register(request):      # this method is used to signup the user
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('loginapp/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                # takes user id and generates the base64 code(uidb64)
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                # Here we receive uidb64, token. By using the "urlsafe_base64_decode"
                # we decode the base64 encoded uidb64 user id.
                # We query the database with user id to get user
                'token': account_activation_token.make_token(user),
                # takes the user object and generates the onetime usable token for the user(token)
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')

    else:
        user_form = UserForm()

    return render(request, 'loginapp/registration.html',
                           {'user_form': user_form})


"""this method is used to login the user"""
def user_login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # authentication of user name and password
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return render(request, 'loginapp/index.html', {})
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'loginapp/login.html', {})


"""this method is used to generate confirmation mail to the user"""

def activate(request, uidb64, token):   # this method is used to generate confirmation mail to the user
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))  # uid: The user’s primary key encoded in base 64.
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # We check the token validation
        user.is_active = True
        user.save()
        login(request, user ,backend='django.contrib.auth.backends.ModelBackend')
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

"""
This class is used to display the all users in rest_framework
"""
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
print(UserViewSet.__doc__)

"""
this class is used for login the rest and create the JWT Token 
 and store the token in redis cache
"""
class RestLogin(CreateAPIView):
    # account and create the JWT token
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened", # give the element what you want in rest api
               "data": {},
               "success": False,
               "username":{}}
        try:
            username = request.data['username']
            if username is None:                   # if username is None
                raise Exception("Username is required") # raise exception Username is required
            password = request.data['password']
            if password is None:
                raise Exception("password is required")
            user = authenticate(username=username, password=password) #validate the password
            print('user-->', user)
            if user:
                if user.is_active:  # check if the user is active or not.
                    payload = {'username': username, 'password': password}
                    jwt_token = {
                        'token': jwt.encode(payload, "Cypher", algorithm='HS256').decode('utf-8')
                    }
                    print(jwt_token)  # print JWT Token
                    """ JWT token stored in cache"""
                    token = jwt_token['token']
                    r.set_token("p3", token) # set the token in redis cache
                    token_val = r.get_token("p3") # get the value of token from cache
                    print("Display The Tokens using get_token()")
                    print(token_val)# print the cache token
                    print("Display the length of Token")
                    len_str = r.length_str("p3")
                    print(len_str) # returns the length of token
                    res['message'] = "Logged in Successfully"
                    res['data'] = token
                    res['success'] = True
                    res['username'] = username
                    return Response(res)  # if active then return response with jWT Token
                else:
                    return Response(res) # else user is not active
            if user is None:
                return Response(res)  # else user is not exist
        except Exception as e:
            print(e)
            return Response(res) #print response as is

""" This method is used to display the all users in JSOn Format"""
def get_users():
    users = User.objects.all().values().order_by('-date_joined')  # or simply .values() to get all fields
    users_list = list(users)
    return JsonResponse(users_list, safe=False)


""" Curd Operation for Notes"""

# create the note list
def note_list(request, template_name='Users/note_list.html'):
    notes = Notes.objects.all() # select the all notes
    data = {}
    data['object_list'] = notes  # stored in dictionaries
    return render(request, template_name, data)

# create the note
def note_create(request, template_name='Users/note_form.html'):
    form = NotesForm(request.POST or None)
    if form.is_valid(): # check form is valid?
        form.save()  # if valid save
        return redirect('Users:note_list')
    return render(request, template_name, {'form': form}) # render the view

# update the notes
def note_update(request, pk, template_name='Users/note_form.html'):
    post = get_object_or_404(Notes, pk=pk)  # post the object
    form = NotesForm(request.POST or None, instance=post)
    if form.is_valid(): # check form is valid?
        form.save() # if valid save
        return redirect('Users:note_list') # redirect the note_list.html
    return render(request, template_name, {'form': form})

# delete the note
def note_delete(request, pk, template_name='Users/note_delete.html'):
    note = get_object_or_404(Notes, pk=pk)
    if request.method=='POST': # if request is post
        note.delete() # note is delete
        return redirect('Users:note_list') # redirect the note list
    return render(request, template_name, {'note': note})

""" Curd Operation for Labels"""

# list the labels
def label_list(request, template_name='Users/labels_list.html'):
    labels = Labels.objects.all() # take the all labels
    data = {}
    data['object_list'] = labels  # stored the labels in dictionaries
    return render(request, template_name, data) # render the template

# create Labels
def label_create(request, template_name='Users/labels_form.html'):
    form = LabelsForm(request.POST or None) # form request with post
    if form.is_valid(): # check form is valid?
        form.save() # if valid save form
        return redirect('Users:labels_list') # redirect the form
    return render(request, template_name, {'form': form})

# Edit labels using Label_update
def label_update(request, pk, template_name='Users/labels_form.html'):
    post = get_object_or_404(Labels, pk=pk) # get the object or 404 error
    form = LabelsForm(request.POST or None, instance=post) # send the request post
    if form.is_valid(): # if form is valid?
        form.save() # if valid then save
        return redirect('Users:labels_list') # redirect the labels_list
    return render(request, template_name, {'form': form})

# delete labels using labels_delete view
def label_delete(request, pk, template_name='Users/labels_delete.html'):
    labels = get_object_or_404(Labels, pk=pk)#get the object or 404 error
    if request.method=='POST': # if request method is post
        labels.delete()  # delete labels
        return redirect('Users:labels_list') # redirect the labels_list
    return render(request, template_name, {'labels': labels})

# view for Upload the images
# def image_view(request):
#     if request.method == 'POST':
#         form = NotesForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('base')
#     else:
#         form = NotesForm()
#     return render(request, 'Users/image.html', {
#         'form': form
#     })