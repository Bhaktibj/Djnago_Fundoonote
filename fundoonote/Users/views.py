from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User

from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework import viewsets, generics  # viewSet is collection of Users
from .tokens import account_activation_token # activate the users account
from .serializers import UserSerializer # import the user serializer to serialize the User data
from .redis import redis_methods  # import the redis_method class from redis file
from .forms import UserForm
from django.shortcuts import render
from .documents import PostDocument
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notes, Label
from .serializers import NotesSerializer, LabelSerializer
import pickle

from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import jwt


r = redis_methods()
"""this method is used to display the home page"""
def home(request):
    return render(request, 'loginapp/home.html', {})


"""this method is used to enter the Users"""

def enter(request):
      return render(request, 'loginapp/index.html', {})

# def keep(request):
#     return render(request, 'Users/base.html',{})

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
@login_required
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
               }
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


""" ****************************Curd Operation for Notes*************************** """

"""Create the Notes"""
class CreateNotes(CreateAPIView):
    serializer_class = NotesSerializer

"""Display the list of Notes"""
class NotesList(APIView):
    try:
        def get(self,request):
            notes = Notes.objects.all()
            data = NotesSerializer(notes, many=True).data
            return Response(data)
    except Exception as e:
        print("Invalid Function")

""" Display the details of list"""
class NotesDetail(APIView):
    try:
        def get(self, request, pk):
            note = get_object_or_404(Notes, pk=pk)
            data = NotesSerializer(note).data
            dict = pickle.dumps(data)  # dump the file
            r.set_token('mydict', dict) # stored the value into key
            print("set data")
            read_dict = r.get_token('mydict')  # read the value
            data1 = pickle.loads(read_dict)  # loads data disk into data1
            print(data1)
            return Response(data)
    except Exception as e:
        print("Something is Happen")

""" Delete the Node """
class NotesDelete(APIView):
    def get(self, request, pk):
        note = Notes.objects.get(pk=pk)
        print(pk)
        try:
            if note.deleted == True:  # if deleted field is true.
                data = note.delete()  # if true then delete
                print(data)
            return Response("Delete the Item")
        except Exception as e:
            print(e)

""" Trash the Note"""
class TrashView(APIView):
    try:
        def get(self,request,pk):
            note = Notes.objects.get(pk=pk)
            try:
                if note.trash == False and note.deleted == True:
                    note.trash = True # if trash = false
                    note.save()
                return Response("Note is Trash")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

""" Archive The Note"""
class ArchiveNotes(APIView):
    try:
        def get(self,request,pk):
            note = Notes.objects.get(pk=pk)
            try:
                if note.deleted == False and note.trash == False:
                    if note.is_archive == False: # Check if trash is false or true
                        note.is_archive = True # if false then set True
                        note.save() # save the note
                    else:
                        return Response("Already archive")
                return Response("Archive is set")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

""" Archive The Note"""
class ReminderNotes(APIView):
    try:
        def get(self,request,pk):
            note = Notes.objects.get(pk=pk)
            try:
                if note.remainder == None: # Check reminder is set or not
                    note.remainder =note.pub_date # if none then set pub_date
                    note.save() # save the note
                else:
                    return Response("Already reminder is set") # if set
                return Response("Reminder is set")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

""" Trash List """
class TrashList(generics.ListAPIView):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('trash',)

""" Archive List"""
class ArchiveList(generics.ListAPIView):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('is_archive',)


""" Create the Label View"""
class CreateLabel(CreateAPIView):    # create label view using APIView
    serializer_class = LabelSerializer

""" Display the List of labels"""
class LabelList(APIView): # display list of labels
    def get(self,request):
        label = Label.objects.all()[:20]
        data = LabelSerializer(label, many=True).data
        return Response(data)

""" Display the detail of label """

class LabelDetail(APIView):
    try:
        def get(self, request, pk):
            label = get_object_or_404(Label, pk=pk)
            data = LabelSerializer(label).data
            """ Stored the data into redis cache"""
            dict = pickle.dumps(data)
            r.set_token('mydict', dict)
            print("set data1")
            read_dict = r.get_token('mydict')
            data1 = pickle.loads(read_dict)
            print(data1)
            return JsonResponse(data) # response in json format
    except Exception as e:
        print(e)

""" Delete Labels"""
class LabelDelete(APIView):
    def get(self, request, pk):
        label = Label.objects.get(pk=pk)
        label.delete()
        return Response("Delete the Item")

""" Pagination for Notes"""
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'results': data
        })

class NotesListPage(ListCreateAPIView):
    serializer_class = NotesSerializer
    pagination_class = CustomPagination
    queryset = Notes.objects.all()


""" ElasticSearch"""
def search(request):
    queryset = Notes.objects.all() # select the all object
    query = Q() # Q() objects make it possible to define and reuse conditions

    for title, value in request.POST.items():
        if value: # if field_name .
            try:
                PostDocument.get_field(title) # display the  fields value if it is match
            except:
                continue
            lookup = "{}__icontains".format(title)
            query |= Q(**{lookup: value})
    queryset = queryset.filter(query)
    return HttpResponse(queryset)

