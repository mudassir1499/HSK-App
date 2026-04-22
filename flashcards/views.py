from .models import GrammarPoint
# List grammar points by level
def grammar_list(request, level=None):
    if level:
        grammar_points = GrammarPoint.objects.filter(level=level).order_by('title')
    else:
        grammar_points = GrammarPoint.objects.all().order_by('level', 'title')
    return render(request, 'flashcards/grammar_list.html', {'grammar_points': grammar_points, 'level': level})

# Grammar point detail view
def grammar_detail(request, pk):
    grammar = GrammarPoint.objects.get(pk=pk)
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
    hard_words = UserWord.objects.filter(user=user, difficulty='hard').select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': hard_words, 'difficulty_label': 'Hard'})

def easy_words(request):
    user = get_user(request)
    easy_words = UserWord.objects.filter(user=user, difficulty='easy').select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': easy_words, 'difficulty_label': 'Easy'})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Word, UserWord

# For this demo we'll use a dummy user if not logged in just so it works without auth setup immediately
def get_user(request):
    if request.user.is_authenticated:
        return request.user
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(username='guest')
    return user

def dashboard(request):
    user = get_user(request)
    user_words = UserWord.objects.filter(user=user)
    
    total_words = Word.objects.count()
    if total_words == 0:
        return render(request, 'flashcards/dashboard.html', {'error': 'No words loaded yet.'})

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
    
    base_query = UserWord.objects.filter(user=user)
    if level:
        base_query = base_query.filter(word__hsk_level=level)
        
    # Get a word that needs review
    due_word = base_query.filter(
        next_review_date__lte=timezone.now()
    ).exclude(status='MASTERED').order_by('next_review_date').first()
    
    # If no review words, get a new word
    if not due_word:
        due_word = base_query.filter(status='NEW').first()
        
    context = {
        'card': due_word,
        'level': level
    }
    return render(request, 'flashcards/study.html', context)

def review_action(request, word_id, action):
    user = get_user(request)
    try:
        user_word = UserWord.objects.get(user=user, id=word_id)
        if action == 'remembered':
            user_word.mark_remembered()
        elif action == 'forgotten':
            user_word.mark_forgotten()
        elif action == 'hard':
            user_word.mark_hard()
    except UserWord.DoesNotExist:
        pass
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('study_session')

def word_list(request):
    words = Word.objects.all().order_by('hsk_level', 'id')
    return render(request, 'flashcards/word_list.html', {'words': words})
