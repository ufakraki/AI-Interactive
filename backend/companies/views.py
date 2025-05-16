# backend/companies/views.py
from rest_framework import viewsets, permissions  # permissions'ı import ettik
from .models import Company
from .serializers import CompanySerializer
from core.permissions import IsCompanyUserOrAdmin
from rest_framework.permissions import IsAuthenticated

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', None)
        
        # Superadmin can see all companies
        if user_role == 'superadmin':
            return Company.objects.all()
            
        # Company admin and regular users can only see their own company
        if user.company:
            return Company.objects.filter(id=user.company.id)
            
        return Company.objects.none()