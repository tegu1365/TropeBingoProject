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
    list_display = ('name', 'description','display_genres')
    fields = ('name', 'description')
    inlines = [GenreInline]

    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    display_genres.short_description = 'Genres'


class BingoSheetAdmin(admin.ModelAdmin):
    model = BingoSheet
    ordering = ('name', 'owner')
    search_fields = ('name',)
    list_display = ('name', 'owner', 'code', 'checked', 'private')
    fields = ('name', 'owner', 'code', 'checked', 'private')


admin.site.register(Genre, GenreAdmin)
admin.site.register(Trope, TropeAdmin)
admin.site.register(BingoSheet, BingoSheetAdmin)
