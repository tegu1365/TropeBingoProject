from django.contrib import admin
from django.contrib.auth.models import User

from .models import Trope, BingoSheet, Genre, Friends, FriendRequest, Type, PersonalTrope


class GenreInline(admin.TabularInline):
    model = Trope.genres.through
    extra = 1

class PersonalTropeGenreInline(admin.TabularInline):
    model = PersonalTrope.genres.through
    extra = 1

class GenreAdmin(admin.ModelAdmin):
    model = Genre
    ordering = ('name',)
    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name',)


class TypeInline(admin.TabularInline):
    model = Trope.types.through
    extra = 1

class PersonalTropeTypeInline(admin.TabularInline):
    model = PersonalTrope.types.through
    extra = 1

class TypeAdmin(admin.ModelAdmin):
    model = Type
    ordering = ('name',)
    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name',)


class TropeAdmin(admin.ModelAdmin):
    model = Trope
    ordering = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('genres', 'types')
    list_display = ('name', 'description', 'display_genres', 'display_types')
    fields = ('name', 'description', 'genres', 'types')
    inlines = [GenreInline, TypeInline]

    def formfield_for_genre(self, db_field, request, **kwargs):
        if db_field.name == 'genres':
            kwargs['queryset'] = Genre.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    def formfield_for_type(self, db_field, request, **kwargs):
        if db_field.name == 'types':
            kwargs['queryset'] = Type.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_types(self, obj):
        return ', '.join([_type.name for _type in obj.types.all()])


class PersonalTropeAdmin(admin.ModelAdmin):
    model = PersonalTrope
    ordering = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('genres', 'types')
    list_display = ('name', 'description', 'owner', 'display_genres', 'display_types')
    fields = ('name', 'description', 'owner', 'genres', 'types')
    inlines = [PersonalTropeGenreInline, PersonalTropeTypeInline]

    def formfield_for_genre(self, db_field, request, **kwargs):
        if db_field.name == 'genres':
            kwargs['queryset'] = Genre.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    def formfield_for_type(self, db_field, request, **kwargs):
        if db_field.name == 'types':
            kwargs['queryset'] = Type.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_types(self, obj):
        return ', '.join([_type.name for _type in obj.types.all()])


class BingoSheetAdmin(admin.ModelAdmin):
    model = BingoSheet
    ordering = ('name', 'owner', 'genre')
    search_fields = ('name', 'genre')
    list_display = ('name', 'owner', 'code', 'checked', 'private', 'genre', 'type', 'bingo_done', 'last_update', 'date_created')
    fields = ('name', 'owner', 'code', 'checked', 'private', 'genre', 'type', 'bingo_done')


class FriendsAdmin(admin.ModelAdmin):
    model = Friends
    ordering = ('owner',)
    search_fields = ('owner',)
    filter_horizontal = ('friends',)
    list_display = ('owner', 'display_friends')
    fields = ('owner', 'friends')

    def formfield_for_friends(self, db_field, request, **kwargs):
        if db_field.name == 'friends':
            kwargs['queryset'] = User.objects.order_by('username')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_friends(self, obj):
        return ', '.join([friend.username for friend in obj.friends.all()])


class FriendRequestAdmin(admin.ModelAdmin):
    model = FriendRequest
    ordering = ('sender',)
    search_fields = ('sender',)
    list_display = ('sender', 'receiver')
    fields = ('sender', 'receiver')


admin.site.register(Genre, GenreAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Trope, TropeAdmin)
admin.site.register(PersonalTrope, PersonalTropeAdmin)
admin.site.register(BingoSheet, BingoSheetAdmin)
admin.site.register(Friends, FriendsAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
