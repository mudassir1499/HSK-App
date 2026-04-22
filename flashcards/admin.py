from django.contrib import admin
from .models import Word, UserWord, UserProfile, GrammarPoint

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('chinese', 'pinyin', 'english', 'hsk_level', 'frequency_rank')
    list_filter = ('hsk_level',)
    search_fields = ('chinese', 'pinyin', 'english')
    ordering = ('hsk_level', 'chinese')
    fieldsets = (
        ('Basic Information', {
            'fields': ('chinese', 'pinyin', 'english', 'hsk_level')
        }),
        ('Character Details', {
            'fields': ('character_breakdown', 'radical', 'stroke_count', 'frequency_rank')
        }),
        ('Learning Content', {
            'fields': ('usage_notes', 'grammar_points', 'example_sentences')
        }),
        ('Related Words', {
            'fields': ('synonyms', 'antonyms')
        }),
    )

@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'status', 'difficulty', 'consecutive_correct', 'next_review_date')
    list_filter = ('status', 'difficulty')
    search_fields = ('user__username', 'word__chinese', 'word__pinyin')
    raw_id_fields = ('user', 'word')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'daily_goal', 'words_studied_today', 'total_words_learned')
    list_filter = ('current_streak',)
    search_fields = ('user__username',)

@admin.register(GrammarPoint)
class GrammarPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'example_cn')
    list_filter = ('level',)
    search_fields = ('title', 'explanation', 'example_cn')
    ordering = ('level', 'title')
