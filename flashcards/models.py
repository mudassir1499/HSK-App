from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Grammar point model for HSK grammar section
class GrammarPoint(models.Model):
    HSK_LEVELS = [
        (1, "HSK 1"),
        (2, "HSK 2"),
        (3, "HSK 3"),
        (4, "HSK 4"),
    ]
    level = models.IntegerField(choices=HSK_LEVELS)
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    detailed_explanation = models.TextField(blank=True)
    example_cn = models.TextField(blank=True)
    example_pinyin = models.TextField(blank=True)
    example_en = models.TextField(blank=True)

    def __str__(self):
        return f"HSK {self.level}: {self.title}"

class Word(models.Model):
    hsk_level = models.IntegerField()
    chinese = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100)
    english = models.TextField()

    def __str__(self):
        return f"{self.chinese} (HSK {self.hsk_level})"

class UserWord(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("LEARNING", "Learning"),
        ("REVIEW", "Review"),
        ("MASTERED", "Mastered")
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    DIFFICULTY_CHOICES = [
        ("normal", "Normal"),
        ("hard", "Hard"),
        ("easy", "Easy"),
    ]
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="normal")
    # Simple SRS tracking
    consecutive_correct = models.IntegerField(default=0)
    next_review_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "word")

    def mark_remembered(self):
        self.consecutive_correct += 1
        
        # Calculate next review date based on consecutive correct
        # simple scale: 1d, 3d, 7d, 14d, 30d
        intervals = [1, 3, 7, 14, 30]
        idx = min(self.consecutive_correct - 1, len(intervals) - 1)
        days_to_add = intervals[idx] if self.consecutive_correct > 0 else 1
        
        self.next_review_date = timezone.now() + timedelta(days=days_to_add)
        
        if self.consecutive_correct > len(intervals):
            self.status = "MASTERED"
        else:
            self.status = "REVIEW"
        self.difficulty = "easy"
        self.save()

    def mark_forgotten(self):
        self.consecutive_correct = 0
        self.status = "LEARNING"
        self.next_review_date = timezone.now() # Review immediately
        self.save()

    def mark_hard(self):
        # Don"t increment consecutive correct, just push to tomorrow to repeat again soon
        self.next_review_date = timezone.now() + timedelta(days=1)
        self.status = "REVIEW"
        self.difficulty = "hard"
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.word.chinese} - {self.status}"
