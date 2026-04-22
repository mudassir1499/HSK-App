from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Word, UserWord, UserProfile
from datetime import date
import json

# For this demo we'll use a dummy user if not logged in just so it works without auth setup immediately
def get_user(request):
    if request.user.is_authenticated:
        return request.user
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(username='guest')
    return user

def get_or_create_profile(user):
    """Get or create user profile for tracking"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.reset_daily_goal()
    return profile

def dashboard(request):
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    # Reset daily goal if new day
    profile.reset_daily_goal()
    
    user_words = UserWord.objects.filter(user=user)
    
    total_words = Word.objects.count()
    if total_words == 0:
        return render(request, 'flashcards/dashboard.html', {
            'error': 'No words loaded yet.',
            'profile': profile
        })

    # Calculate overall statistics
    total_mastered = user_words.filter(status='MASTERED').count()
    total_learning = user_words.filter(status='LEARNING').count()
    total_due = user_words.filter(next_review_date__lte=timezone.now(), status__in=['LEARNING', 'REVIEW']).count()
    total_new = user_words.filter(status='NEW').count()
    
    # Get recent activity (last 7 days)
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    recent_reviews = user_words.filter(
        last_reviewed__gte=week_ago,
        last_reviewed__isnull=False
    ).count()
    
    # Calculate accuracy
    total_reviewed = user_words.filter(times_reviewed__gt=0).count()
    if total_reviewed > 0:
        avg_accuracy = sum(uw.calculate_retention_rate() for uw in user_words.filter(times_reviewed__gt=0)) / total_reviewed
    else:
        avg_accuracy = 0
    
    levels = []
    for level in range(1, 5):
        level_words = user_words.filter(word__hsk_level=level)
        if level_words.exists():
            levels.append({
                'level': level,
                'total': level_words.count(),
                'mastered': level_words.filter(status='MASTERED').count(),
                'learning': level_words.filter(status='LEARNING').count(),
                'review_due': level_words.filter(next_review_date__lte=timezone.now()).count()
            })
    
    context = {
        'total_words': total_words,
        'levels': levels,
        'profile': profile,
        'stats': {
            'total_mastered': total_mastered,
            'total_learning': total_learning,
            'total_due': total_due,
            'total_new': total_new,
            'recent_reviews': recent_reviews,
            'avg_accuracy': round(avg_accuracy, 1),
            'goal_progress': profile.get_goal_progress(),
        }
    }
    return render(request, 'flashcards/dashboard.html', context)

def init_user_words(request):
    """Utility to initialize UserWord models for all existing Words for the user."""
    user = get_user(request)
    words = Word.objects.all()
    existing_user_words = UserWord.objects.filter(user=user).values_list('word_id', flat=True)
    
    new_user_words = []
    for word in words:
        if word.id not in existing_user_words:
            new_user_words.append(UserWord(user=user, word=word))
            
    if new_user_words:
        UserWord.objects.bulk_create(new_user_words)
        
    return redirect('dashboard')

def study_session(request, level=None):
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    base_query = UserWord.objects.filter(user=user)
    if level:
        base_query = base_query.filter(word__hsk_level=level)
        
    # Get a word that needs review (prioritize forgotten/hard words)
    due_word = base_query.filter(
        next_review_date__lte=timezone.now(),
        status__in=['LEARNING', 'REVIEW']
    ).exclude(status='MASTERED').order_by('next_review_date', '-times_incorrect').first()
    
    # If no review words, get a new word
    if not due_word:
        due_word = base_query.filter(status='NEW').first()
    
    # Update session tracking
    if due_word:
        due_word.studied_in_session = False
        due_word.session_correct = None
        due_word.save()
    
    context = {
        'card': due_word,
        'level': level,
        'profile': profile,
        'words_studied_today': profile.words_studied_today,
        'daily_goal': profile.daily_goal,
    }
    return render(request, 'flashcards/study.html', context)

def review_action(request, word_id, action):
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    try:
        user_word = UserWord.objects.get(user=user, id=word_id)
        
        # Track if this is first time learning
        if user_word.first_learned is None and action == 'remembered':
            user_word.first_learned = timezone.now()
        
        if action == 'remembered':
            user_word.mark_remembered()
            profile.words_studied_today += 1
            profile.update_streak()
        elif action == 'forgotten':
            user_word.mark_forgotten()
            profile.words_studied_today += 1
            profile.update_streak()
        elif action == 'hard':
            user_word.mark_hard()
            profile.words_studied_today += 1
            profile.update_streak()
            
        profile.save()
        
    except UserWord.DoesNotExist:
        pass
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('study_session')

def word_list(request):
    user = get_user(request)
    words = Word.objects.all().order_by('hsk_level', 'id')
    
    # Get user's progress for each word
    user_word_map = {uw.word_id: uw for uw in UserWord.objects.filter(user=user)}
    
    word_data = []
    for word in words:
        user_word = user_word_map.get(word.id)
        word_data.append({
            'word': word,
            'user_word': user_word,
        })
    
    return render(request, 'flashcards/word_list.html', {'word_data': word_data})

# Grammar views
def grammar_list(request, level=None):
    from .models import GrammarPoint
    if level:
        grammar_points = GrammarPoint.objects.filter(level=level).order_by('title')
    else:
        grammar_points = GrammarPoint.objects.all().order_by('level', 'title')
    return render(request, 'flashcards/grammar_list.html', {'grammar_points': grammar_points, 'level': level})

def grammar_detail(request, pk):
    from .models import GrammarPoint
    grammar = get_object_or_404(GrammarPoint, pk=pk)
    return render(request, 'flashcards/grammar_detail.html', {'grammar': grammar})

def study_hard_words(request):
    user = get_user(request)
    hard_word = UserWord.objects.filter(user=user, difficulty='hard').order_by('next_review_date').first()
    return render(request, 'flashcards/study.html', {'card': hard_word, 'level': None, 'difficulty_mode': 'hard'})

def study_easy_words(request):
    user = get_user(request)
    easy_word = UserWord.objects.filter(user=user, difficulty='easy').order_by('next_review_date').first()
    return render(request, 'flashcards/study.html', {'card': easy_word, 'level': None, 'difficulty_mode': 'easy'})

def hard_words(request):
    user = get_user(request)
    hard_words_list = UserWord.objects.filter(user=user, difficulty='hard').select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': hard_words_list, 'difficulty_label': 'Hard'})

def easy_words(request):
    user = get_user(request)
    easy_words_list = UserWord.objects.filter(user=user, difficulty='easy').select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': easy_words_list, 'difficulty_label': 'Easy'})

def stats_view(request):
    """Detailed statistics view"""
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    user_words = UserWord.objects.filter(user=user)
    
    # Get words grouped by status
    new_count = user_words.filter(status='NEW').count()
    learning_count = user_words.filter(status='LEARNING').count()
    review_count = user_words.filter(status='REVIEW').count()
    mastered_count = user_words.filter(status='MASTERED').count()
    
    # Get difficulty distribution
    hard_count = user_words.filter(difficulty='hard').count()
    normal_count = user_words.filter(difficulty='normal').count()
    easy_count = user_words.filter(difficulty='easy').count()
    
    # Get retention rate distribution
    high_retention = user_words.filter(times_reviewed__gt=0).filter(
        times_correct__gte=models.F('times_reviewed') * 0.8
    ).count()
    
    # Get today's activity
    today = date.today()
    today_reviews = user_words.filter(
        last_reviewed__date=today,
        last_reviewed__isnull=False
    ).count()
    
    context = {
        'profile': profile,
        'stats': {
            'new_count': new_count,
            'learning_count': learning_count,
            'review_count': review_count,
            'mastered_count': mastered_count,
            'hard_count': hard_count,
            'normal_count': normal_count,
            'easy_count': easy_count,
            'high_retention': high_retention,
            'today_reviews': today_reviews,
        }
    }
    return render(request, 'flashcards/stats.html', context)
