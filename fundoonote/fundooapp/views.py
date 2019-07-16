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
from .service import BotoService
import boto3
from .decorators import app_login_required
from django.core.mail import send_mail
import json


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

import logging
log =logging.getLogger(__name__)
#*********************************Registration for User using Rest API******************************
class RestUserRegister(CreateAPIView):
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
class Login(CreateAPIView):
    """
    this class is used for login the rest and create the JWT Token
     and store the token in redis cache
    """
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
            response = {
                "message": "something bad happened",
                "data": {},
                "success": False
            }
            try:
                username = request.data['username']
                password = request.data['password']
                if password is None and username is None:
                    log.info('username, password, email is required',username)
                    raise Exception("Username & password is required")
                if username is None:                    # if username is None
                    log.info('username is required',username)
                    raise Exception("Username is required") # raise exception Username is required
                if password is None:
                    log.info('password is required')
                    raise Exception("password is required",password)
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
                        log.info("warning")
                        return Response(response)  # if active then return response with jWT Token
                    else:
                        return Response(response) # else user is not active
                if user is None:
                    return Response(response)  # else user is not exist
            except:
                return Response(response) # print response as is



#**********************************Curd Operation on Notes*****************************************

class CreateNotes(CreateAPIView):
    """This class View is used Create the Note using Post method"""
    serializer_class = NotesSerializer
    def post(self, request,*args, **kwargs):
        res ={'message':"Something bad happened",
              'data':{},
              'mail_data':'Mail is not sent',
              'total_mail':0,
              'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the Try block") # try block
            log.info("Request the data")
            data = request.data         # request the user data
            # Create an Notes from the above data
            log.info("serialize the data")
            serializer = NotesSerializer(data=data) # serialize the data
            log.info("validation of serializer")
            if serializer.is_valid(raise_exception=True): # check the serializer is valid or not
                log.info("save the serializer")
                serializer.save()  # save serializers
                res['message']= "Successfully created note"
                res['success']= True
                res[ 'data' ] = serializer.data
                log.info("dumps the json data into string")
                note_data = json.dumps(res) # convert the json data into string format
                mail_count = 0  # mail count =0
                log.info("taking the collaborator field")
                for i in serializer.data['collaborator']: # take the collaborator list
                    user = User.objects.get(id=i) # take the user
                    if user:
                            send_mail(          # user then send the mail
                            'Sending Note to the user',
                            note_data,
                            request.user.email,
                            [str(user.email)],
                            fail_silently=False,
                            )
                    log.info("count the mail")
                    mail_count +=1
                res['mail_data']="Sent the mail successfully"# get serialize data
                res['total_mail']=mail_count
                log.info("Return the response")
            return Response(res,status=status.HTTP_201_CREATED) # created status_code 201
        except:
            log.error("Return the error")
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

print("CreateNotes:",CreateNotes.__doc__)

#****************************************List of  the Notes ****************************************
class NotesList(APIView):
    """This class is used to Display the list of Notes"""
    def get(self,request):
       res = {'message': "Something bad happened",
              'data':{},
               'success': False}
       try:
            print("***************************************************************")
            log.info("select the object")
            notes = Notes.objects.all() # select the all object
            log.info("serialize the object")
            data = NotesSerializer(notes, many=True).data # serialize the data
            res[ 'message' ] = "Successfully display the note"
            res[ 'success' ] = True
            res[ 'data' ] = data
            log.info("List of the Notes")
            return Response(res, status=200) # return the data
       except:
              log.error("Empty List")
              return Response(res, status=404) #if try block is False
print("NoteList:",NotesList.__doc__)

#**************************************Display the specific note********************************
class NotesDetail(APIView):
    """ Display the details of list and store data into redis cache"""
    def get(self,request, pk):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            print("***************************************************************")
            log.info("select the object")
            note = get_object_or_404(Notes, pk=pk)
            log.info("check the note.pin is true or what")
            if note.pin is True:
                log.info("serialize the data")
                data = NotesSerializer(note).data
                dict_data = pickle.dumps(data)  # dump the file
                r.set_value('dict', dict_data) # stored the value into key
                print("set data")
                read_dict = r.get_value('dict')  # read the value
                log.info("Store data into redis cache")
                data1 = pickle.loads(read_dict)  # loads data disk into data1
                print(data1)
                res[ 'message' ] = "Successfully display the note"
                res[ 'success' ] = True
                res[ 'data' ] = data
            else:
                log.warning("First make the note.pin == true")
                return Response("Please First make the note.pin is true and pin the note")
            log.info("return the successfully response")
            return Response(res, status=200)
        except:
            log.error("not not found")
            return Response(res,status=404)

#************************************************Delete the note************************************
class NotesDelete(APIView):
    """ This class is used to Delete the Note"""
    def delete(self, request, pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            print("***************************************************************")
            log.info("get the specific note")
            note = Notes.objects.get(pk=pk) # check pk value
            log.info("If note.deleted ==true")
            if note.deleted is True:
                note.delete()  # if true then delete
                res[ 'message' ] = "Successfully deleted the note"
                res[ 'success' ] = True
                log.info("deleted the object")
                return Response(res,status=200)
            else:
                log.warning("Please make the note.deleted = true")
                return Response("Note deleted =False,Please make note.deleted = True")
        except:
           log.error("note is does not exist")
           return Response(res,status=404) # if try block is false
print("NoteDelete:",NotesDelete.__doc__)

#********************************************update the note***************************************
class NotesUpdate(APIView):
    """ API endpoint that allows users to be viewed or edited."""
    serializer_class = NotesSerializer
    model = Notes
    def put(self,request, pk,*args, **kwargs):
        res = {'message': "Something bad happened",
               'data':{},
               'success': False}
        try:
            print("***************************************************************")
            log.info("get the specific note")
            note = Notes.objects.get(pk=pk) # get the note
            log.info("request the data")
            data = request.data
            log.info("serialize the data")
            serializer = NotesSerializer(note, data=data, partial=True)
            log.info("check the is valid")
            if serializer.is_valid(raise_exception=True): # check the serializer is valid or not?
                log.info("save the serializer")
                serializer.save() # if valid save
                res[ 'message' ] = "Successfully Updated note"
                res['data']= serializer.data
                res[ 'success' ] = True
                log.info("update the note")
                return Response(res, status=200)
        except:
            log.error("Note is not found")
            return Response(res, status=404)

# *********************************************Trash the note***********************************
class TrashView(APIView):
    """ Trash the Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:                  # try block
            print("***************************************************************")
            log.info("Enter the try block and select the note")
            note = Notes.objects.get(pk=pk)
            log.info("if note is deleted the trash the note")
            if note.trash is False and note.deleted is True: # check trash and delete field
                note.trash = True # if trash = false
                log.info("note is save")
                note.save()
                res[ 'message' ] = "Successfully Trash the note"
                res[ 'success' ] = True
                log.info("return successfully response")
            return Response(res, status=200) # if trash is false then set trash = True
        except:
            log.error("Note not found")
            return Response(res, status=404) # except block

# **************************************************Archive the notes*******************************
class ArchiveNotes(APIView):
    """ Archive The Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            print("***************************************************************")
            log.info("enter the try block")
            note = Notes.objects.get(pk=pk)
            log.info("if note is not deleted the archive the note otherwise no")
            if note.deleted == False and note.trash == False:
                if note.is_archive is False: # Check if trash is false or true
                    log.warning("note is archive is false then set archive ==true")
                    note.is_archive = True # if false then set True
                    note.save() # save the note
                    res[ 'message' ] = "Successfully Trash the note"
                    res[ 'success' ] = True
                else:
                    log.info("note is already archive")
                    return Response("Already archive")
            else:
                log.warning("note is already deleted")
                return Response("Note is already deleted or trash")
            log.info("return successfully response")
            return Response(res, status=200)
        except:
            log.error("note is not found")
            return Response(res,status=404)
#***********************************************set reminder to note*****************************
class ReminderNotes(APIView):
    """ set Reminder for Note The Note"""
    def get(self,request,pk):
        res = {'message': "Something bad happened",
               'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the try block")
            note = Notes.objects.get(pk=pk)
            if note.remainder is None: # Check reminder is set or not
                note.remainder =note.pub_date # if none then set pub_date
                note.save() # save the note
                data = NotesSerializer(note).data  # serialize the object
                created_id = data['created_By']
                user = User.objects.get(id=created_id)  # take the user
                send_mail(  # user then send the mail
                    'Sending Note',
                    "Sending Notification successfully",
                    request.user.email,  # from current logged user
                    [ str(user.email) ], # to address who are created the note
                    fail_silently=False,
                )
                res[ 'message' ] = "Successfully Set Reminder note"
                res[ 'success' ] = True

            else:
                return Response("Already reminder is set") # if set
            return Response(res, status=200)  # return the Ok response
        except:
            return Response(res, status=404) # return the not found response

# *****************************Curd Operations on label**************************************************"""

class CreateLabel(CreateAPIView):
    """ Create the Label View using post method"""
    serializer_class = LabelSerializer
    def post(self, request, *args, **kwargs):
        res ={'message':"Something bad happened",
              'data': {},
              'success': False}
        try:
            print("***************************************************************")
            log.info("enter the try block")
            data = request.data   # request the data
            log.info("serialize the data")
            serializer = LabelSerializer(data=data) # validate the request data
            log.info("check if serializer is valid or not")
            if serializer.is_valid(raise_exception=True): # if serializer is valid
                serializer.save()                         # save serializer
                res['message']= "Successfully created Label"
                res['success']= True
                res['data']=serializer.data
                log.info("return the response")
            return Response(res,status=status.HTTP_201_CREATED) # return accept response
        except:
            log.info("enter the except block")
            log.error("label is not created")
            return Response(res,status=status.HTTP_400_BAD_REQUEST) # return bad response

# ******************************************list the label**************************************
class LabelList(APIView):
    """ Display the List of labels"""
    def get(self,request):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the try block")
            label = Label.objects.all()
            log.info("serialize the object")
            data = LabelSerializer(label, many=True).data # getting the specific label
            """ Stored the data into redis cache"""
            dict_data = pickle.dumps(data)  # dump the data pickle into dictionary
            r.set_value('dict', dict_data)  # store the data into key value
            print("set data")
            read_dict = r.get_value('dict')  # get the data from redis cache
            log.info("stored the label into redis cache")
            data1 = pickle.loads(read_dict)  # load the pickle
            print(data1)
            res[ 'message' ] = "Successfully Display the list Label"
            res[ 'success' ] = True
            res['data'] = data
            log.info("return positive response")
            return Response(res, status=200) # return the Ok response
        except:
            log.info("Enter the except block") # return the not found response
            log.error("Empty list")
            return Response(res, status=404)
#******************************************Update and detail the note******************************
class LabelUpdateDetail(APIView):
    """ Display the detail of label and Updated """
    serializer_class = LabelSerializer
    def get(self, request, pk):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the try block")
            label = get_object_or_404(Label, pk=pk)
            log.info("Serialize the object")
            data = LabelSerializer(label).data
            """ Stored the data into redis cache"""
            dict_data = pickle.dumps(data)  # dump the data pickle into dictionary
            r.set_value('dict', dict_data) # store the data into key value
            print("set data")
            read_dict = r.get_value('dict') # get the data from redis cache
            log.info("Stored the data into redis cache")
            data1 = pickle.loads(read_dict) # load the pickle
            print(data1)
            res[ 'message' ] = "Successfully display Label"
            res[ 'success' ] = True
            res[ 'data' ] = data
            log.info("Return the successfully Response")
            return Response(res, status=200) # response in json format
        except:
            log.info("Enter the try block")
            log.error("label is not found")
            return Response(res, status=404) # return the not found response

    def put(self,request, pk, ):
        res = {'message': "Something bad happened",
               'data': {},
               'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the try block")
            label = Label.objects.get(pk=pk) # get the note
            log.info("request the data")
            data = request.data
            log.info("serialize the data")
            serializer = LabelSerializer(label, data=data, partial=True,)
            if serializer.is_valid(raise_exception=True): # check the serializer is valid or not?
                serializer.save() # if valid save
                res[ 'message' ] = "Successfully Updated Label"
                res[ 'success' ] = True
                res[ 'data' ] = serializer.data
                log.info("Return the Response")
                return Response(res, status=200) # return the Ok response
        except:
            log.error('label is not found')
            return Response(res,status=400) # return the not found  response

#****************************************Delete the specific note************************************************
class LabelDelete(APIView):
    """ Delete particular label"""
    def delete(self, request, pk):  # delete the labels using pk
        res = {'message': "Something bad happened",
               'success': False}
        try:
            print("***************************************************************")
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
            print("***************************************************************")
            log.info("Provide the data ")
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
            log.error("if invalid data")
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

#***************************************Getting label from Notes**********************************
class LabelFromNotes(APIView):
    """ This view is used to show the label detail from Notes """
    def get(self, request, pk):
        res = {'message': "Something bad happened",
               'data':{},
               'success': False}
        try:
            print("***************************************************************")
            log.info("Enter the Try block")
            note = Notes.objects.get(pk=pk) # getting specific note object
            log.info("Serialize the note object")
            data = NotesSerializer(note).data # serialize the object
            log.info("getting the id label id from note data")
            label =data['label']              # getting the label object from notes
            log.info("If label is there")
            if label:
                log.info("validate the label id with label tabel")
                label_obj = Label.objects.get(id=label)  #checking the label object is there in label model
                log.info("serialize the label_data object")
                label_data = LabelSerializer(label_obj).data # is there then serialize the label object
                log.info("getting the user id from label_data")
                user_id = label_data['created_By']   # getting the user_id
                log.info("validate the user_id")
                user = User.objects.get(pk=user_id )
                res[ 'message' ] = "Successfully Showed the Label from Notes:"
                res['data']['Title']=data['title'] # print the notes title
                res['data']['note_id']=note.pk   # prints the note id
                res['data']['label_id']=label_data['id']  # prints the label id
                res['data']['Label']=label_data['text'] # print the label text
                res['data']['created_By']=user.username # print the username
                res[ 'success' ] = True
                log.info("Return the response")
            return Response(res,status=200) # give the successfully response
        except:
            log.info("enter the except block")
            log.error("not found notes")
            return Response(res,status=404) # if try block is false


# ***************************************S3 AWS Implementation*************************************
class create_aws_bucket(CreateAPIView):
    """ create bucket using boto3 services method"""
    serializer_class = AWSModelSerializer
    # Assign these values before running the program
    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened",
                "success": False}
        try:                              # enter try block
            print("***************************************************************")
            log.info("Enter the try block")
            log.info("request the bucket_name")
            bucket_name = request.data['bucket_name']  # request the bucket_name
            if bucket_name is None:
                raise Exception("Bucket name must be unique")
            log.info("request the region")             # bucket name must be unique
            region = request.data['region']
            log.info("Create the aws bucket")
            aws = AWSModel.objects.create(bucket_name=bucket_name, region=region)
            aws.save()
            log.info("stored the bucket")
            log.info("call the aws create bucket")
            if boto.create_bucket(bucket_name=bucket_name, region=region):
                log.info('Created bucket {bucket_name} '
                             'in region {region}')
                res[ 'message' ] = "Bucket Is Created Successfully...",
                res[ 'success' ] = True,
                log.info("Return the Response")
            return Response(res)
        except:
            log.error("Enter the except block")
            return Response(res)

#********************************************Delete Buckets*******************************************
class delete_aws_bucket(APIView):
    """ Delete bucket using boto3 service from rest api"""
    def delete(self, request, pk):
        res = {"message": "something bad happened",
               "success": False}
        try:
            print("***************************************************************")
            log.info("Enter the try block")
            bucket = AWSModel.objects.get(pk=pk) # check pk value
            log.info("Getting the bucket id from restapi")
            data = AWSModelSerializer(bucket).data  # serialize the object
            bucket_name = data[ 'bucket_name' ]
            log.info("call listing object function")
            objects = boto.list_bucket_objects(bucket_name) # listing object from bucket function
            if objects is not None:   # if objects is not none
                return Response("Bucket is not empty") # return response please make the bucket is empty
            else:
                if bucket.delete():        # if bucket is deleted then
                    log.info("call the aws delete bucket function")
                    if boto.delete_bucket(bucket_name):       # delete the bucket from AWS
                        logging.info('{bucket_name} was deleted')
                        res[ 'message' ] = "Bucket Is Deleted Successfully",
                        res[ 'success' ] = True,
                        log.info("Return the Response")
                return Response(res,status=200)  # return the response
        except:
            log.error("Invalid function")  # Return the bad response
            return Response(res)

#**************************************List of the Buckets*****************************************
class Bucket_List(APIView):
    """display all the buckets in Rest API"""
    def get(self,request):
        try:
            print("***************************************************************")
            log.info("Enter the try block")  # enter the try block
            log.info("select all object")
            bucket = AWSModel.objects.all() # select the object
            log.info("Serialize the object")
            data = AWSModelSerializer(bucket, many=True).data  # serialize the objects
            log.info("Return the response")
            return Response(data) # return Response
        except:
            log.error("Empty list")
            return Response("invalid or empty")

#*******************************************Upload_S3 profile************************************
@csrf_exempt
def s3_upload(request,pk):
    response = {
        'message':'Bad request or empty file can not be uploaded',
        'success' : False,
        'status_code' :400,
        'bucket_name':''
    }
    try:
        print("***************************************************************")
        log.info("Enter the try block")
        log.info("request the post method")
        if request.method == 'POST':
            log.info("request the aws objects")
            note = AWSModel.objects.get(pk=pk)  # getting specific note object
            log.info("serialize the object in json data")
            data = AWSModelSerializer(note).data  # serialize the object
            log.info("access the bucket name from rest _ap model")
            bucket_name = data['bucket_name']
            log.info("upload the profile using postman form data")
            uploaded_file = request.FILES.get('document')
            log.info("if uploaded file name is None")
            if uploaded_file is None:
                return JsonResponse(response)
            else:
                log.info("set the file name")
                file_name = 'image.jpeg'
                log.info("call the boto3 object")
                s3_client = boto3.client('s3')
                log.info("upload the image")
                s3_client.upload_fileobj(uploaded_file, bucket_name, Key=file_name)
                response['message'] = "Image successfully uploaded"
                response['status_code'] = 200
                response['success'] = True
                response['bucket_name']= bucket_name
                log.info("Return the Response ")
                return JsonResponse(response)
        else:
            log.info("return the bad response")
            return JsonResponse(response)
    except:
        return JsonResponse(response)


#**************************************ElasticSearch Implementation ******************
class NotesDocumentViewSet(DocumentViewSet):
    """ Search the Notes using ElasticSearch"""
    document = NotesDocument # documents
    serializer_class = NotesDocumentSerializer # serializer class
    log.info("filter backends")
    filter_backends = [
        FilteringFilterBackend, # backend filter
        OrderingFilterBackend,   # ordering filter based on title
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        FunctionalSuggesterFilterBackend
    ]

    # Define search fields
    log.info("pagination class filter")
    pagination_class = LimitOffsetPagination
    # search fields : title, description, color, remainder
    log.info("search filter")
    search_fields = (
    'title',
    'description',
    'color',
    'remainder',
    )

# Filter fields
    log.info("filter fields")
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
    log.info("Ordering filters")
# Define ordering fields
    ordering_fields = {
    'title': 'title.raw',
    'description': 'description.raw',
        'color':'color.raw',
        'remainder':'remainder.raw',

    }
  # suggests filter
    log.info("fuctional suggester filter")
    functional_suggester_fields = {
        'title':'title.raw',
        'description':'description.raw',
        'color': 'color.raw',
        'remainder': 'remainder.raw',
    }


#**********************************Implementation of Search Filter***********************

class TrashList(generics.ListAPIView):
    """ List Trash note using django filter backend """
    log.info("list of the trash notes")
    queryset = Notes.objects.all() # select all the object
    serializer_class = NotesSerializer # serializer
    log.info("loading the django_filter backend")
    filter_backends = (DjangoFilterBackend,) # set the django filter
    filter_fields = ('trash',)

class ArchiveList(generics.ListAPIView): # use teh ListApi view
    """ List Archive note using django filter backend"""
    log.info("List of the archive notes")
    queryset = Notes.objects.all()  # select all objects
    serializer_class = NotesSerializer # serializer class
    log.info("loading the django_filter backend")
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('is_archive',) # set the filter which you want filter

class UserListView(generics.ListAPIView):
    """Search the user using django backend search filter"""
    log.info("List of the users based on username, id fields notes")
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

