import imghdr

from boto3.s3.inject import upload_file
from django.conf.locale import es
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, LOOKUP_QUERY_GT, \
    LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE, SUGGESTER_TERM, SUGGESTER_PHRASE, SUGGESTER_COMPLETION, \
    FUNCTIONAL_SUGGESTER_COMPLETION_PREFIX
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, OrderingFilterBackend, \
    DefaultOrderingFilterBackend, SearchFilterBackend, CompoundSearchFilterBackend, FunctionalSuggesterFilterBackend, \
    SuggesterFilterBackend
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework import viewsets, generics, status

from .tokens import account_activation_token # activate the users account
from .serializers import UserSerializer, RegisterSerializer, AWSModelSerializer, NotesDocumentSerializer
from .redis import redis_methods # import the redis_method class from redis file
from .forms import UserForm
from django.shortcuts import render
from .documents import NotesDocument
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notes, Label, AWSModel
from .serializers import NotesSerializer, LabelSerializer
import pickle

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import jwt
import logging
from .service import BotoService
import os
import boto3
from boto3.s3.transfer import S3Transfer
from .decorators import app_login_required


r = redis_methods()
boto= BotoService()
"""this method is used to display the home page"""
def home(request):
    return render(request, 'fundooapp/home.html', {})

"""this method is used to enter the fundooapp"""

def enter(request):
    return render(request, 'fundooapp/index.html', {})

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
            message = render_to_string('fundooapp/acc_active_email.html', {
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

    return render(request, 'fundooapp/registration.html',
                           {'user_form': user_form})


"""this method is used to login the user"""
@csrf_exempt
def user_login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        try:
            response = {
                "message": "something bad happened",
                "data": {},
                "success": False
            }
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username is None and password is None:
                raise Exception('Username and password is required')
            if username is None:
                raise Exception('Username is required')
            if password is None:
                raise Exception('Password is required')
            # authentication of user name and password
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    payload = {'username': username, 'password': password}
                    jwt_token = {
                        'token': jwt.encode(payload, "Cypher", algorithm='HS256').decode('utf-8')
                    }
                    print(jwt_token)  # print JWT Token
                    """ JWT token stored in cache"""
                    token = jwt_token[ 'token' ]
                    print(token)
                    login(request, user)
                    print(user.username)
                    return render(request, 'fundooapp/index.html', {}, response)
                else:
                    return HttpResponse("Your account was inactive.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username, password))
                return HttpResponse("Invalid login details given")
        except:
            return render(request, 'fundooapp/user_login.html', {})
    else:
        return render(request, 'fundooapp/user_login.html', {})


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


class UserViewSet(viewsets.ModelViewSet):
    """This Class is used to create the user"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
print("UserViewSet:",UserViewSet.__doc__)

""" This method is used to display all users list"""
@method_decorator(app_login_required, name='dispatch')
def get_users():
    users = User.objects.all().values().order_by('-date_joined')  # or simply .values() to get all fields
    users_list = list(users)
    return JsonResponse(users_list, safe=False)


#**********************************Curd Operation on Notes*************************** """

class CreateNotes(APIView):
    """This class View is used Create the Note using Post method"""
    serializer_class = NotesSerializer
    def post(self, request):
        res ={'message':"Something bad happened",
              'success': False}
        try:
            notes = request.data
            # Create an Notes from the above data
            serializer = NotesSerializer(data=notes)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                res['message']= "Successfully created note"
                res['success']= True
            return Response(res,status=status.HTTP_201_CREATED)
        except:
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

print("CreateNotes:",CreateNotes.__doc__)

class NotesList(APIView):
    """Display the list of Notes"""
    def get(self,request):
       res = {'message': "Something bad happened",
              'data':{},
               'success': False}
       try:
            notes = Notes.objects.all() # select the all object
            data = NotesSerializer(notes, many=True).data # serialize the data
            res[ 'message' ] = "Successfully display the note"
            res[ 'success' ] = True
            res[ 'data' ] = data
            return Response(res, status=200) # return the data
       except:
              return Response(res, status=404) #if try block is False

class NotesDetail(APIView):
    """ Display the details of list and store data into redis cache"""
    def get(self, request, pk):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            note = get_object_or_404(Notes, pk=pk)
            data = NotesSerializer(note).data
            dict_data = pickle.dumps(data)  # dump the file
            r.set_value('dict', dict_data) # stored the value into key
            print("set data")
            read_dict = r.get_value('dict')  # read the value
            data1 = pickle.loads(read_dict)  # loads data disk into data1
            print(data1)
            res[ 'message' ] = "Successfully display the note"
            res[ 'success' ] = True
            res[ 'data' ] = data
            return Response(res, status=200)
        except:
            return Response(res,status=404)

class NotesDelete(APIView):
    """ Delete the Note"""
    def delete(self, request, pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            note = Notes.objects.get(pk=pk) # check pk value
            if note.deleted == True:
                note.delete()  # if true then delete
                res[ 'message' ] = "Successfully deleted the note"
                res[ 'success' ] = True
                return Response(res,status=200)
            else:
                return Response("Note deleted =False,Please make note.deleted = True")
        except:
           return Response(res,status=404) # if try block is false

class NotesUpdate(APIView):
    """ API endpoint that allows users to be viewed or edited."""
    def put(self,request, pk):
        res = {'message': "Something bad happened",
               'data':{},
               'success': False}
        try:
            note = Notes.objects.get(pk=pk) # get the note
            data = request.data
            serializer = NotesSerializer(note, data=data, partial=True)
            if serializer.is_valid(raise_exception=True): # check the serializer is valid or not?
                serializer.save() # if valid save
                res[ 'message' ] = "Successfully Updated note"
                res['data']= serializer.data
                res[ 'success' ] = True
                return Response(res, status=200)
        except:
            return Response(res, status=404)

class TrashView(APIView):
    """ Trash the Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:                  # try block
            note = Notes.objects.get(pk=pk)
            if note.trash == False and note.deleted == True: # check trash and delete field
                note.trash = True # if trash = false
                note.save()
                res[ 'message' ] = "Successfully Trash the note"
                res[ 'success' ] = True
            return Response(res, status=200) # if trash is false then set trash = True
        except:
            return Response(res, status=404) # except block

class ArchiveNotes(APIView):
    """ Archive The Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            note = Notes.objects.get(pk=pk)
            if note.deleted == False and note.trash == False:
                if note.is_archive == False: # Check if trash is false or true
                    note.is_archive = True # if false then set True
                    note.save() # save the note
                    res[ 'message' ] = "Successfully Trash the note"
                    res[ 'success' ] = True
                else:
                    return Response("Already archive")
            else:
                return Response("Note is already deleted or trash")
            return Response(res, status=200)
        except:
            return Response(res,status=404)

class ReminderNotes(APIView):
    """ set Reminder for Note The Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            note = Notes.objects.get(pk=pk)
            if note.remainder == None: # Check reminder is set or not
                note.remainder =note.pub_date # if none then set pub_date
                note.save() # save the note
                res[ 'message' ] = "Successfully Trash the note"
                res[ 'success' ] = True
            else:
                return Response("Already reminder is set") # if set
            return Response(res, status=200)
        except:
            return Response(res, status=404)


# *****************************Curd Operations on label**********************************"""

class CreateLabel(APIView):    # create label view using APIView
    """ Create the Label View using post method"""
    serializer_class = LabelSerializer
    def post(self, request):
        res ={'message':"Something bad happened",
              'success': False}
        try:
            data = request.data
            # Create an Notes from the above data
            serializer = LabelSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                res['message']= "Successfully created Label"
                res['success']= True
            return Response(res,status=status.HTTP_201_CREATED)
        except:
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class LabelList(APIView):
    """ Display the List of labels"""
    def get(self,request):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:

            label = Label.objects.all()
            data = LabelSerializer(label, many=True).data
            """ Stored the data into redis cache"""
            dict_data = pickle.dumps(data)  # dump the data pickle into dictionary
            r.set_value('dict', dict_data)  # store the data into key value
            print("set data")
            read_dict = r.get_value('dict')  # get the data from redis cache
            data1 = pickle.loads(read_dict)  # load the pickle
            print(data1)
            res[ 'message' ] = "Successfully Display the list Label"
            res[ 'success' ] = True
            res['data'] = data
            return Response(res, status=200)
        except:
            return Response(res, status=404)

class LabelUpdateDetail(APIView):
    """ Display the detail of label and Updated """
    def get(self, request, pk):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            label = get_object_or_404(Label, pk=pk)
            data = LabelSerializer(label).data
            """ Stored the data into redis cache"""
            dict_data = pickle.dumps(data)  # dump the data pickle into dictionary
            r.set_value('dict', dict_data) # store the data into key value
            print("set data")
            read_dict = r.get_value('dict') # get the data from redis cache
            data1 = pickle.loads(read_dict) # load the pickle
            print(data1)
            res[ 'message' ] = "Successfully display Label"
            res[ 'success' ] = True
            res[ 'data' ] = data
            return Response(res, status=200) # response in json format
        except:
            return Response(res, status=404)

    def put(self,request, pk):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            label = Label.objects.get(pk=pk) # get the note
            data = request.data
            serializer = LabelSerializer(label, data=data, partial=True)
            if serializer.is_valid(raise_exception=True): # check the serializer is valid or not?
                serializer.save() # if valid save
                res[ 'message' ] = "Successfully Updated Label"
                res[ 'success' ] = True
                res[ 'data' ] = serializer.data
                return Response(res, status=200)
        except:
            return Response(res,status=400)

class LabelDelete(APIView):
    """ Delete particular label"""
    def delete(self, request, pk):  # delete the labels using pk
        res = {'message': "Something bad happened",
               'success': False}
        try:
            label = Label.objects.get(pk=pk) # check pk value
            label.delete()  # call delete function
            res[ 'message' ] = "Successfully deleted Label"
            res[ 'success' ] = True
            return Response(res,status=200)
        except:
            return Response(res,status=404) # if try block is false


#**************************************Pagination View *******************************************"""
class CustomPagination(PageNumberPagination):
    """ This class is used to the for pagination purpose"""
    page_size = 15 # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        try:
            return Response({
                'links': {
                    'next': self.get_next_link(), # next link
                    'previous': self.get_previous_link() # previous page link
                },
                'count': self.page.paginator.count, # total count of the objects
                'page_size': self.page_size, # size of the page
                'results': data # result
            })
        except:
            return Response("invalid value pagination") # if user enter the invalid data

class NotesListPage(ListCreateAPIView):
    """ Set pagination for Notes"""
    serializer_class = NotesSerializer # Serializer
    pagination_class = CustomPagination # Use the CustomPagination class here
    queryset = Notes.objects.all() # select objects all

class LabelListPage(ListCreateAPIView):
    """ Set pagination for Label"""
    serializer_class = LabelSerializer # Serializer
    pagination_class = CustomPagination # Use the CustomPagination class her
    queryset = Label.objects.all()

#*********************************Registration for User using Rest API******************************
class RestUserRegister(APIView):
    """
    this class is used for Register the rest User and create the JWT Token
     and store the token in redis cache
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened",
                "data": {},
                "success": False}
        try:
            username = request.data['username']  # getting the username
            email = request.data['email']   # getting the email id
            password = request.data['password']     # getting the password
            if username and email and password is not "":   # condition
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False
                user.save()
                    #current_site = get_current_site(request)
                message = render_to_string('fundooapp/acc_active_email.html', {
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
                return Response(res,status=201) # if try block is True return the response
        except:
            return Response(res,status=400)


#***********************************Rest Login for User***********************************
class Login(APIView):
    """
    this class is used for login the rest and create the JWT Token
     and store the token in redis cache
    """
    # account and create the JWT token
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        try:
            response = {
                "message": "something bad happened",
                "data": {},
                "success": False
            }
            username = request.data['username']
            password = request.data['password']
            if password is None and username is None:
                raise Exception("Username & password is required")
            if username is None:                    # if username is None
                raise Exception("Username is required") # raise exception Username is required
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
                    response['message'] = "Logged in Successfully"
                    response['data'] = token
                    response['success'] = True
                    return Response(response)  # if active then return response with jWT Token
                else:
                    return Response(response) # else user is not active
            if user is None:
                return Response(response)  # else user is not exist
        except:
            return Response(response) # print response as is


# ***************************************S3 AWS Implementation***************************
class create_aws_bucket(CreateAPIView):
    """ create bucket using boto3 services method"""
    serializer_class = AWSModelSerializer
    # Assign these values before running the program
    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened",
                "success": False}
        bucket_name = request.data['bucket_name']  # getting the username
        region = request.data['region']
        if boto.bucket_exists(bucket_name):
            return Response("Bucket is already exist")
        else:
            aws = AWSModel.objects.create(bucket_name=bucket_name, region=region)
            aws.save()
        # Create a bucket in a specified region
            if boto.create_bucket(bucket_name=bucket_name, region=region):
                logging.info(f'Created bucket {bucket_name} '
                        f'in region {region}')
                res[ 'message' ] = "Bucket Is Created Successfully...",
                res[ 'success' ] = True,
            return Response(res)

#***************************************Delete Buckets********************************
class delete_aws_bucket(APIView):
    """ Delete bucket using boto3 service from rest api"""
    def delete(self, request, pk):
        res = {"message": "something bad happened",
               "success": False}
        try:
            bucket = AWSModel.objects.get(pk=pk) # check pk value
            bucket.delete()  # call delete function
            if boto.delete_bucket(bucket.bucket_name):
                logging.info(f'{bucket.bucket_name} was deleted')
                res[ 'message' ] = "Bucket Is Deleted Successfully",
                res[ 'success' ] = True,
            return Response(res,status=200)
        except:
            return Response(res)

#**********************************List of the Buckets*****************************
class Bucket_List(APIView):
    """display all the buckets in Rest API"""
    def get(self,request):
        try:
            bucket = AWSModel.objects.all() # select the object
            data = AWSModelSerializer(bucket, many=True).data
            return Response(data) # return Response
        except:
            return Response("invalid or empty")


#**************************************S3 Upload files*******************************
# upload the image using boto3 services
def upload_s3(request):
    try:
        # local directory path
        local_directory = '/home/shadowk/PycharmProjects/Programs_BridgeLab/FundooProject/fundoonote/fundooapp/media'
        # boto3 service
        transfer = S3Transfer(boto3.client('s3'))
        bucket = 'django-s3-assets2' # S3 existing bucket
        for root, dirs, files in os.walk(local_directory): # local directory
            for filename in files:
                local_path = os.path.join(root, 'image3.jpeg')
                relative_path = os.path.relpath(local_path, local_directory)
                s3_path = os.path.join('S3 Directory',relative_path) # creating the folder in AWS
                if filename.endswith('.pdf'):
                    transfer.upload_file(local_path, bucket, s3_path)
                else:
                    transfer.upload_file(local_path, bucket, s3_path,extra_args={'ACL': 'private'})
        return HttpResponse ("Image is Upload")
    except:
        return HttpResponse("Invalid data")

#**************************************ElasticSearch Implementation ******************
class NotesDocumentViewSet(DocumentViewSet):
    """ Search the Notes using ElasticSearch"""
    document = NotesDocument # documents
    serializer_class = NotesDocumentSerializer # serializer class

    filter_backends = [
        FilteringFilterBackend, # backend filter
        OrderingFilterBackend,   # ordering filter based on title
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        FunctionalSuggesterFilterBackend
    ]

    # Define search fields
    pagination_class = LimitOffsetPagination
    # search fields : title, description, color, remainder
    search_fields = (
    'title',
    'description',
    'color',
    'remainder',
    )

# Filter fields
    filter_fields = {
        'id':{
        'field': 'id',
        'lookups': [
        LOOKUP_FILTER_RANGE,
        LOOKUP_QUERY_IN, # In a given list.
        LOOKUP_QUERY_GT, # Greater than.
        LOOKUP_QUERY_GTE, # Greater than or equal to.
        LOOKUP_QUERY_LT, # Less than.
        LOOKUP_QUERY_LTE, # Less than or equal to.
    ],
    },
        'title': 'title.raw',
        'description': 'description.raw',
        'color':'color.raw',
        'remainder':'remainder.raw',
    }

# Define ordering fields
    ordering_fields = {
    'title': 'title.raw',
    'description': 'description.raw',
        'color':'color.raw',
        'remainder':'remainder.raw',

    }
  # suggests filter
    functional_suggester_fields = {
        'title':'title.raw',
        'description':'description.raw',
        'color': 'color.raw',
        'remainder': 'remainder.raw',
    }


#**********************************Implementation of Search Filter***********************

class TrashList(generics.ListAPIView):
    """ List Trash note using django filter backend """
    queryset = Notes.objects.all() # select all the object
    serializer_class = NotesSerializer # serializer
    filter_backends = (DjangoFilterBackend,) # set the django filter
    filter_fields = ('trash',)

class ArchiveList(generics.ListAPIView): # use teh ListApi view
    """ List Archive note using django filter backend"""
    queryset = Notes.objects.all()  # select all objects
    serializer_class = NotesSerializer # serializer class
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('is_archive',) # set the filter which you want filter

class UserListView(generics.ListAPIView):
    """Search the user using django backend search filter"""
    queryset = User.objects.all() # select all object
    serializer_class = UserSerializer # user serializer
    filter_backends = (filters.SearchFilter,) # use the backend filter
    search_fields = ('username','id')  # search user detail by using username field

class NotesListView(generics.ListAPIView):
    """Search the Notes using django backend search filter"""
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer # define the serializer_class
    filter_backends = (filters.SearchFilter,) # use the backend filter
    search_fields = ('title','id') # search the note detail by using title field

# *********************************** Search Operations using Form****************************************
def search(request):
    """ Search the note using form"""
    q = request.GET.get('q', None)
    notes = ''
    if q is None or q is "":
        notes = Notes.objects.all() # select the all objects
    elif q is not None:
        notes = Notes.objects.filter(Q(title__icontains=q) | Q(id__icontains=q) | Q(color__icontains=q))
    return render(request, 'fundooapp/search.html', {'notes': notes})

