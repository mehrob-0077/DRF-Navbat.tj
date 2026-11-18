from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Branch
from .serializers import BranchSerializer


class BranchListView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]


class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        organization = serializer.validated_data['organization']
        if organization.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied()
        serializer.save()


class BranchDetailView(generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]


class BranchUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        branch = self.get_object()
        if branch.organization.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied()
        serializer.save()


class BranchDeleteView(generics.DestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.organization.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied()
        instance.delete()
