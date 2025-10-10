from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from izgora.models import Category
from .models import User, QrCode
import qrcode
from io import BytesIO


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'name', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'username', 'name', 'payment_status', 'role', 'password',
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    fields = ('name', 'slug', 'created')
    readonly_fields = ('created',)


class QrCodeInline(admin.TabularInline):
    model = QrCode
    extra = 0
    fields = ('link', 'qr_preview', 'created')
    readonly_fields = ('qr_preview',)

    def qr_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100" style="border:1px solid #ccc; border-radius:5px;" />'
            )
        return "QR mavjud emas"

    qr_preview.short_description = "QR Preview"

    def save_model(self, request, obj, form, change):
        if obj.link:
            qr_image = qrcode.make(obj.link)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f"qr_{obj.user.username}_{obj.id or 'new'}.png"
            obj.image.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save_model(request, obj, form, change)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    inlines = [CategoryInline, QrCodeInline]

    list_display = ('id', 'username', 'payment_status', 'name', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    ordering = ('username',)
    search_fields = ('username', 'name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'role', 'payment_status', 'subdomain', 'secret_key')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'role', 'password1', 'password2'),
        }),
    )
