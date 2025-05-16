from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from companies.models import Company
from .models import User
from companies.serializers import CompanySerializer
from .serializers import UserSerializer, PasswordChangeSerializer, CustomTokenObtainPairSerializer
from .permissions import IsCompanyUserOrAdmin
from rest_framework.permissions import IsAuthenticated

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CompanyView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]
    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) == 'superadmin':
            companies = Company.objects.all()
        else:
            companies = Company.objects.filter(id=getattr(user, 'company_id', None))
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

class UserView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]
    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) == 'superadmin':
            users = User.objects.all()
        else:
            users = User.objects.filter(company=getattr(user, 'company', None))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCompanyUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'superadmin':
            return User.objects.all()
        return User.objects.filter(company=getattr(user, 'company', None))

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)