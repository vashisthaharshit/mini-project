from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenBackendError, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from django.db import IntegrityError

@api_view(['POST'])
def registerUser(request):
    data = request.data
    username = data.get('username')
    role = data.get('role', 'user') 

    if User.objects.filter(username=username).exists():
        return Response({
            "Message": "User already exists with the given username, try another."
        })
    
    serializer = UserSerializer(data=data)
    if not serializer.is_valid():
        return Response({
            "Message": serializer.errors
        })
    
    user = serializer.save()
    
    try:
        user_profile = UserProfile.objects.create(user=user, role=role)
    except IntegrityError:
        user_profile = UserProfile.objects.get(user=user)
        user_profile.role = role
        user_profile.save()
    
    refresh = RefreshToken.for_user(user)
    response = Response({
        "Message": "User registered successfully.",
        "Refresh": str(refresh),
        "Access": str(refresh.access_token)
    })
    
    response.set_cookie(key='jwt', value=str(refresh.access_token), httponly=True, secure=True, samesite='None')
    
    return response


@api_view(['POST'])
def loginUser(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = User.objects.filter(username=username).first()
    
    if not user or not user.check_password(password):
        return Response({
            "Message": "Invalid username or password."
        })
    
    refresh = RefreshToken.for_user(user)
    response = Response({
        "Message": "User logged in successfully.",
        "Refresh": str(refresh),
        "Access": str(refresh.access_token)
    })
    
    response.set_cookie(key='jwt', value=str(refresh.access_token), httponly=True, secure=True, samesite='None')
    
    return response


@api_view(['GET'])
def authenticated_user(request):

    jwt = request.COOKIES.get('jwt')

    if not jwt:
        return Response({
            "Message": "Unauthorized uesr"
        })

    return Response({
        "Message": "Authorized user."
    })


@api_view(['POST'])
def logoutUser(request):
    response = Response({
        "Message": "User logged out successfully."
    })
    
    response.delete_cookie('jwt', path='/', domain=None)
    return response


@api_view(['POST', 'GET'])
def createBlog(request):
    if request.method == 'POST':
        jwt = request.COOKIES.get('jwt')
    
        if jwt is None:
            return Response({"Message": "Unauthorized access"})

        try:
            token = AccessToken(jwt)
            user_id = token['user_id']
            user = User.objects.get(id=user_id)
        except (InvalidToken, TokenBackendError):
            return Response({"Message": "Invalid token"})
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"})

        data = request.data
        serializer = BlogSerializer(data=data)

        if serializer.is_valid():
            blog = serializer.save()
            blog.author = user 
            blog.save() 
            
            return Response({
                "Message": "Blog created successfully",
                "Payload": serializer.data
            })
        
        return Response({"Message": serializer.errors})
    

    else:
        jwt = request.COOKIES.get('jwt')
        
        if jwt is None:
            return Response({"Message": "Unauthorized access"})

        try:
            token = AccessToken(jwt)
            user_id = token['user_id']
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
        except (InvalidToken, TokenBackendError):
            return Response({"Message": "Invalid token"})
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"})
        except UserProfile.DoesNotExist:
            return Response({"Message": "User profile does not exist"})
        except TokenError:
            return Response({"Message": "Token is invalid or expired"})


        blogs = Blog.objects.filter(author=user)

        serializer = BlogSerializer(blogs, many=True)
        return Response({
            "Message": "Blogs",
            "Payload": serializer.data
        })


@api_view(['GET'])
def getBlogById(request, id):
    try:
        blog = Blog.objects.get(id=id)
    except Blog.DoesNotExist:
        return Response({"Message": "Blog not found"})
    
    jwt = request.COOKIES.get('jwt')
    if jwt is None:
        return Response({"Message": "Unauthorized access"})

    try:
        token = AccessToken(jwt)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
    except (InvalidToken, TokenBackendError):
        return Response({"Message": "Invalid token"})
    except User.DoesNotExist:
        return Response({"Message": "User does not exist"})
    except UserProfile.DoesNotExist:
        return Response({"Message": "User profile does not exist"})
    
    if blog.author == user:
        serializer = BlogSerializer(blog)
        return Response({
            "Message": "Blog details",
            "Payload": serializer.data
        })
    else:
        return Response({"Error": "You are not authorized to view this blog"})


@api_view(['GET'])
def adminPage(request):
    jwt = request.COOKIES.get('jwt')
        
    if jwt is None:
        return Response({"Message": "Unauthorized access"})

    try:
        token = AccessToken(jwt)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
    except (InvalidToken, TokenBackendError):
        return Response({"Message": "Invalid token"})
    except User.DoesNotExist:
        return Response({"Message": "User does not exist"})
    except UserProfile.DoesNotExist:
        return Response({"Message": "User profile does not exist"})
    except TokenError:
        return Response({"Message": "Token is invalid or expired"})

    if user_profile.role == 'admin':
        return HttpResponse("Admin page")
    else:
        return Response({
            "Error": "You don't have admin role features"
        })
    

@api_view(['GET'])
def normalPage(request):
    jwt = request.COOKIES.get('jwt')
        
    if jwt is None:
        return Response({"Message": "Unauthorized access"})

    try:
        token = AccessToken(jwt)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
    except (InvalidToken, TokenBackendError):
        return Response({"Message": "Invalid token"})
    except User.DoesNotExist:
        return Response({"Message": "User does not exist"})
    except UserProfile.DoesNotExist:
        return Response({"Message": "User profile does not exist"})
    except TokenError:
        return Response({"Message": "Token is invalid or expired"})

    if user_profile.role != 'admin':
        return HttpResponse("Normal page")
    else:
        return Response({
            "Error": "You don't have normal role features"
        })