from django.contrib import admin
from .models import Project, Transaction

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'author')
    search_fields = ('title', 'author')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'project', 'amount', 'verified')
    search_fields = ('email', 'project__title')
    list_filter = ('verified',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
