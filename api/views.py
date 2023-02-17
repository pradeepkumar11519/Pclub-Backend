from django.shortcuts import render
from rest_framework.generics import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from .helpers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializer import *
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from .emails import *
from .pagination import *
# Create your views here.
class VerifyOTP(APIView):   #Making a Class Based View Called Verify OTP 
    def post(self,request):    #making a post reuqest
            data = request.data  #collecting the data sent by the frontend
            serializer = VerifyOTPSerializer(data = data)    #Using the Serializer Class VerifyOTPSerializer and sending in the data to the serializer
            if serializer.is_valid():    #checing is serializer accepts the data
                email = serializer.data["email"]     #obtaining the email of the person from the serialized data
                otp = serializer.data["otp"]         #obtaining the otp from the serialized data
                user = User.objects.filter(email=email)    #getting or filtering the user with email equal to the email sent by the frontend 
                if not user.exists():                      #if the user is not present in the database then he is unauthorized
                    return Response("UnAuthorized",status=status.HTTP_401_UNAUTHORIZED)
                if user[0].otp != otp:                     #if otp is wrong then asking the user to retry thus sending a http response of a bad request 
                    return Response("Wrong Otp Please Retry",status=status.HTTP_400_BAD_REQUEST)
                user = user.first()                        #since filter gives list of objects so we filter out the first element from the list using the .first() 
                user.email_is_verified = True             #since otp is verified as it had no obstacles so making the email_is_verified Field True
                user.save()                    #saving the user instance
            return Response('OTP Succesfully Verified',status=status.HTTP_200_OK)    #senidng a http response of 200 saying the user that his otp is verified





class Signup(APIView):                            #making a class Based view using APIView
    def post(self,request):                       #making a Post Reuqest
            data = request.data                   #obtaining the data sent by the frontend
            serializer = UserSerializer(data = data)         #Serializing(converting objects into certain datatypes here its json and vice versa) data given by frontend
            if serializer.is_valid():                        #if serializer accepts the incomming data without any error
                serializer.save()                            #saving the user instance with the serializer
                send_otp_via_email(serializer.data["email"])     #sending the otp through a function called send_otp_via_email in the .emails file
                return Response({"email":serializer.data["email"]},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):                         #making a class based view called Login Using APIView                                  
    def post(self, request):                 #creating a post request
        try:                                    
            username = request.data['username']        #extracting the username from the data sent by frontend
            password = request.data['password']        #extracting the password from the data sent by frontend
            email = request.data['email']               #extracting the email from the data sent by frontend

            # checking for errors
            user = User.objects.filter(username=username).first()           #getting the user with the given username as he must have been signed up before and stored in the database

            if user is None:                                       #if the user is not found then he wasnt signed up and error is sent back to the frontend
                return Response({'error': 'invalid username or password'}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):                  #if the user has entered wrong password then an error is sent to the frontend
                return Response({'error': 'invalid username or password'}, status=status.HTTP_404_NOT_FOUND)
            if user.email_is_verified == False:                   #if the user has signed up but hasnt verified his email yet so again an error is sent to the frontend
                return Response({'error': 'invalid username or password'}, status=status.HTTP_404_NOT_FOUND)
            else:
                if email == user.email:              #checking if the email sent by the frontend is same as the email stored in the database
                    refresh = RefreshToken.for_user(user)               #providing a refresh token for the user
                    user.last_login = datetime.datetime.now()           #updating his last login time
                    user.save()                                        #saving the user instance
                    return Response({                                 #sending a resposne to the frontend,providing the frontend the access and refresh token along with users details without his password
                        'message': 'login successfull',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'username': user.username,
                        'last_login_date': getdate(),
                        'last_login_time': gettime(),
                        'email': user.email},
                        status=status.HTTP_200_OK)

                else:             #if the email sent by the frontend is not equal to the email of the user stored in that database then send a error to the frontend
                    return Response({'errors': 'email not matched'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'errors':'Some Error Occured'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListBlogs(ListAPIView):          #using a class based view to get all the blogs from the database
    pagination_class = MyBlogPagination           #using pagination so that our frontend can fetch 3 blogs at a time.the idea of pagination is that as we keep scrolling down the frontend keeps fetching 3 blogs.so suppose we have 9 blogs,1st frontend fetches 3 blogs and then again 3 and again 3 and then it stops
    serializer_class = BlogSerializer              #using the Blog Serializer present in .serializer
    queryset = Blog.objects.all()                 #queryset is important because it tells the backend what objects are to be sent to the frontend



class ListSearchedBlogs(ListAPIView):          #using a class based view to get all the blogs from the database
    filter_backends = [SearchFilter]              #having a search filter to enable the user to search among multiple blogs
    search_fields = ['title','desc']               #parameter that the user can search on is title and desc only
    serializer_class = BlogSerializer              #using the Blog Serializer present in .serializer
    queryset = Blog.objects.all()                  #queryset is important because it tells the backend what objects are to be sent to the frontend


class CreateBlogs(CreateAPIView):      #making a class Based View to CreateBlogs
    authentication_classes = [JWTAuthentication]           #using simplejwt for authentication so user can add blogs only when he is logged in
    permission_classes = [IsAuthenticated]                 #saying that the user can get permission only if he is authenticated.well not to worry a lot about this because simplejwt handles all of this
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()


class UpdateBlogs(UpdateAPIView):            #making a class based view for updating blogs
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()

class DestroyBlogs(DestroyAPIView):           #making a class based view for deleting blogs
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()

    
class RetrieveBlogs(RetrieveAPIView):            #making a class based view for getting a single blog based on its id
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()


class ListComment(ListAPIView):              
    serializer_class = CommentSerializer
    def get_queryset(self,**kwargs):
        return BlogComment.objects.filter(blog = self.kwargs['pk'])

class CreateComment(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = BlogComment.objects.all()
    

class DeleteUpdateComment(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = BlogComment.objects.all()
    serializer_class = CommentSerializer