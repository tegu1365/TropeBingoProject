from django.contrib import admin
from .models import Trope, BingoSheet, Genre


class GenreInline(admin.TabularInline):
    model = Trope.genres.through
    extra = 1


class GenreAdmin(admin.ModelAdmin):
    model = Genre
    ordering = ('name',)
    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name',)


class TropeAdmin(admin.ModelAdmin):
    model = Trope
    ordering = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('genres',)
    list_display = ('name', 'description', 'display_genres')
    fields = ('name', 'description', 'genres')
    inlines = [GenreInline]

    def formfield_for_genre(self, db_field, request, **kwargs):
        if db_field.name == 'genres':
            kwargs['queryset'] = Genre.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    display_genres.short_description = 'Genres'


class BingoSheetAdmin(admin.ModelAdmin):
    model = BingoSheet
    ordering = ('name', 'owner', 'genre')
    search_fields = ('name', 'genre')
    list_display = ('name', 'owner', 'code', 'checked', 'private', 'genre')
    fields = ('name', 'owner', 'code', 'checked', 'private', 'genre')


admin.site.register(Genre, GenreAdmin)
admin.site.register(Trope, TropeAdmin)
admin.site.register(BingoSheet, BingoSheetAdmin)
