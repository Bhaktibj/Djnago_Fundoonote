import short_url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework import viewsets, generics, settings
from rest_framework.permissions import IsAuthenticated

from .tokens import account_activation_token # activate the users account
from .serializers import UserSerializer, RegisterSerializer, LinkSerializer
from .redis import redis_methods  # import the redis_method class from redis file
from .forms import UserForm
from django.shortcuts import render, redirect
from .documents import PostDocument
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notes, Label, Link
from .serializers import NotesSerializer, LabelSerializer
import pickle

from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import jwt


r = redis_methods()
"""this method is used to display the home page"""
def home(request):
    return render(request, 'loginapp/home.html', {})


"""this method is used to enter the Users"""

def enter(request):
      return render(request, 'loginapp/index.html', {})

def link(request):
    return render(request,'loginapp/link_form.html')

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
            #current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('loginapp/acc_active_email.html', {
                'user': user,
                'domain': '127.0.0.1:8000',
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


#***************This method is used to display the all users in JSOn Format***********
def get_users():
    users = User.objects.all().values().order_by('-date_joined')  # or simply .values() to get all fields
    users_list = list(users)
    return JsonResponse(users_list, safe=False)


#**********************************Curd Operation for Notes*************************** """

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

""" Display the details of list and store data into redis cache"""
class NotesDetail(APIView):
    def get(self, request, pk):
        try:
            note = get_object_or_404(Notes, pk=pk)
            data = NotesSerializer(note).data
            dict = pickle.dumps(data)  # dump the file
            r.set_value('mydict', dict) # stored the value into key
            print("set data")
            read_dict = r.get_value('mydict')  # read the value
            data1 = pickle.loads(read_dict)  # loads data disk into data1
            print(data1)
            return Response(data)
        except:
            return Response("Note Does Not Exist")

""" Delete the Node """
class NotesDelete(APIView):
    def get(self, request, pk):
        try:
            note = Notes.objects.get(pk=pk)
            print(pk)
            if note.deleted == True:  # if deleted field is true.
                data = note.delete()  # if true then delete
                print(data)
            return Response("Delete the Item")
        except:
           return Response("Note does not Exist")

""" Trash the Note"""
class TrashView(APIView):
    def get(self,request,pk):
        try:                  # try block
            note = Notes.objects.get(pk=pk)
            if note.trash == False and note.deleted == True: # check trash and delete field
                note.trash = True # if trash = false
                note.save()
            return Response("Note is Trash") # if trash is false then set trash = True
        except:
            return Response("Notes  does not exist") # except block

""" Archive The Note"""
class ArchiveNotes(APIView):
    def get(self,request,pk):
        try:
            note = Notes.objects.get(pk=pk)
            if note.deleted == False and note.trash == False:
                if note.is_archive == False: # Check if trash is false or true
                    note.is_archive = True # if false then set True
                    note.save() # save the note
                else:
                    return Response("Already archive")
            else:
                return Response("Note is already deleted or trash")
            return Response("Archive is set")
        except:
            return Response("Notes does not exist")

""" set Reminder for Note The Note"""
class ReminderNotes(APIView):
    def get(self,request,pk):
        try:
            note = Notes.objects.get(pk=pk)
            if note.remainder == None: # Check reminder is set or not
                note.remainder =note.pub_date # if none then set pub_date
                note.save() # save the note
            else:
                return Response("Already reminder is set") # if set
            return Response("Reminder is set")
        except:
            return Response(" Note does not Exist")


# *****************************Curd Operations on label**********************************"""

""" Create the Label View"""
class CreateLabel(CreateAPIView):    # create label view using APIView
    serializer_class = LabelSerializer

""" Display the List of labels"""
class LabelList(APIView): # display list of all labels
    def get(self,request):
        label = Label.objects.all()
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
            r.set_value('mydict', dict)
            print("set data1")
            read_dict = r.get_value('mydict')
            data1 = pickle.loads(read_dict)
            print(data1)
            return Response(data) # response in json format
    except Exception as e:
        print(e)

""" Delete Labels"""
class LabelDelete(APIView):
    def get(self, request, pk):
        label = Label.objects.get(pk=pk)
        label.delete()
        return Response("Delete the Item")


#**************************************Pagination View *******************************************"""
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(), # next link
                'previous': self.get_previous_link() # previous page link
            },
            'count': self.page.paginator.count, # total count of the page
            'page_size': self.page_size, # size of the page
            'results': data # result
        })

""" Set pagination for Notes"""
class NotesListPage(ListCreateAPIView): # class base view function
    serializer_class = NotesSerializer # Serializer
    pagination_class = CustomPagination # Use the CustomPagination class here
    queryset = Notes.objects.all() # select objects all

""" Set pagination for Label"""
class LabelListPage(ListCreateAPIView): # class base view function
    serializer_class = LabelSerializer # Serializer
    pagination_class = CustomPagination # Use the CustomPagination class her
    queryset = Label.objects.all()

#*********************************Registration for User using Rest API******************************
class RestUserRegister(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened",
               "data": {},
               "success": False}
        username = request.data['username']  # getting the username
        email = request.data['email']   # getting the email id
        password = request.data['password']     # getting the password
        if username and email and password is not "":   # condition
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()
            #current_site = get_current_site(request)
            message = render_to_string('loginapp/acc_active_email.html', {
                'user': user,
                'domain': '127.0.0.1:8000',
                # takes user id and generates the base64 code(uidb64)
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                # Here we receive uidb64, token. By using the "urlsafe_base64_decode"
                # we decode the base64 encoded uidb64 user id.
                # We query the database with user id to get user
                'token': account_activation_token.make_token(user),
                # takes the user object and generates the onetime usable token for the user(token)
            })
            mail_subject = 'Activate your account...'
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            if send_email:
                    payload = {'username': username, 'password': password,'email':email}
                    jwt_token = {
                        'token': jwt.encode(payload, "Cypher", algorithm='HS256').decode('utf-8')
                    }
                    print(jwt_token)  # print JWT Token
                    """ JWT token stored in cache"""
                    token = jwt_token[ 'token' ]
                    r.set_value("p3", token)  # set the token in redis cache
                    token_val = r.get_value("p3")  # get the value of token from cache
                    print("Display The Tokens using get_token()")
                    print(token_val)  # print the cache token
                    print("Display the length of Token")
                    len_str = r.length_str("p3")
                    print(len_str)  # returns the length of token
                    res['message'] = "Register Successfully...Please activate your Account",
                    res[ 'data' ] = token,
                    res[ 'success' ] = True,
            return Response(res)
        else:
            return Response(res)

#***********************************Rest Login for User***********************************
"""
this class is used for login the rest and create the JWT Token 
 and store the token in redis cache
"""
class RestLogin(APIView):
    # account and create the JWT token
    permission_classes = (IsAuthenticated,)
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
                    r.set_value("p3", token) # set the token in redis cache
                    token_val = r.get_value("p3") # get the value of token from cache
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

#*****************************************Create Short URLs**************************
""" Create the link"""
class LinkCreate(CreateAPIView):
    serializer_class = LinkSerializer

""" List the all links"""
class LinkList(APIView): # display list of all labels
    def get(self,request):
        link = Link.objects.all()
        data = LinkSerializer(link, many=True).data
        return Response(data)

""" Delete the Link"""
class LinkDelete(APIView):
    def get(self, request, pk):
        link = Link.objects.get(pk=pk)
        link.delete()
        return Response("Delete the Link")

#**********************************Implementation of Search Filter***********************

""" Trash List using django filter backend """
class TrashList(generics.ListAPIView):
    queryset = Notes.objects.all() # select all the object
    serializer_class = NotesSerializer # serializer
    filter_backends = (DjangoFilterBackend,) # set the django filter
    filter_fields = ('trash',)

""" Archive List using django filter backend"""
class ArchiveList(generics.ListAPIView): # use teh ListApi view
    queryset = Notes.objects.all()  # select all objects
    serializer_class = NotesSerializer # serializer class
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('is_archive',) # set the filter which you want filter

""" Display the notes by User"""

class UserListView(generics.ListAPIView):
    queryset = User.objects.all() # select all object
    serializer_class = UserSerializer # user serializer
    filter_backends = (filters.SearchFilter,) # use the backend filter
    search_fields = ('username',)  # search user detail by using username field

class NotesListView(generics.ListAPIView):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer # define the serializer_class
    filter_backends = (filters.SearchFilter,) # use the backend filter
    search_fields = ('title',) # search the note detail by using title field

# ***********************************ElasticSearch****************************************
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

