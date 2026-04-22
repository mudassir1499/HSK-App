# HSK Books & TTS Feature Guide

## Overview
This feature adds comprehensive reading materials with HSK Standard Course Books (levels 1-6), complete with Chinese text, pinyin, English translations, and built-in Text-to-Speech (TTS) functionality.

## New Models

### Book
- **title**: Name of the book (e.g., "HSK Standard Course 1")
- **hsk_level**: HSK level (1-6)
- **description**: Brief description of book content
- **cover_image**: Optional book cover image

### Chapter
- **book**: Foreign key to parent Book
- **chapter_number**: Sequential chapter number
- **title**: Chapter title
- **summary**: Brief summary of chapter content

### TextSegment
- **chapter**: Foreign key to parent Chapter
- **order**: Sequence order within chapter
- **chinese_text**: Chinese characters (Simplified)
- **pinyin**: Pinyin with tone marks
- **english_translation**: English translation
- **audio_file**: Optional pre-recorded audio (falls back to TTS)
- **key_words**: Many-to-many link to Vocabulary words

## Features

### 📚 Book Library
- Browse all HSK books by level
- View chapter counts and segment counts
- Beautiful card-based UI

### 📖 Chapter Reader
- Select chapters from any book
- See chapter summaries
- One-click start reading

### 🔊 Text-to-Speech
- **Browser-based TTS**: Uses Web Speech API (no server processing needed)
- **Chinese Voice**: Automatically selects Chinese voice when available
- **Playback Controls**: 
  - Listen buttons for each text section
  - Replay button
  - Play/Pause with Space bar
- **Keyboard Navigation**:
  - `←` Arrow: Previous segment
  - `→` Arrow: Next segment  
  - `Space`: Play/Pause audio

### 📝 Learning Display
- **Chinese Section**: Large characters with listen button
- **Pinyin Section**: Tone-marked pinyin with listen button
- **English Section**: Full translation
- **Key Vocabulary**: Related words from your vocabulary list

## Adding Content via Django Admin

### Step 1: Create a Book
1. Go to `/admin/flashcards/book/`
2. Click "Add Book"
3. Enter:
   - Title: "HSK Standard Course 1"
   - HSK Level: 1
   - Description: "Beginner level textbook covering basic greetings and introductions"
4. Save

### Step 2: Add Chapters
1. Go to `/admin/flashcards/chapter/`
2. Click "Add Chapter"
3. Select the book
4. Enter:
   - Chapter Number: 1
   - Title: "Hello"
   - Summary: "Learn to greet people and introduce yourself"
5. Save

### Step 3: Add Text Segments
1. Go to `/admin/flashcards/textsegment/`
2. Click "Add Text Segment"
3. Select the chapter
4. Enter:
   - Order: 1
   - Chinese Text: 你好，我叫李明。
   - Pinyin: Nǐ hǎo, wǒ jiào Lǐ Míng.
   - English Translation: Hello, my name is Li Ming.
5. Optionally link key vocabulary words
6. Save

Repeat for all segments in the chapter.

## Example Data Structure

```python
# Book
title = "HSK Standard Course 1"
hsk_level = 1
description = "Complete beginner course"

# Chapter 1
chapter_number = 1
title = "Meeting New People"
summary = "Basic greetings and self-introduction"

# Text Segment 1
order = 1
chinese_text = "你好！"
pinyin = "Nǐ hǎo!"
english_translation = "Hello!"

# Text Segment 2
order = 2
chinese_text = "你叫什么名字？"
pinyin = "Nǐ jiào shénme míngzi?"
english_translation = "What's your name?"

# Text Segment 3
order = 3
chinese_text = "我叫王老师。"
pinyin = "Wǒ jiào Wáng lǎoshī."
english_translation = "My name is Teacher Wang."
```

## URLs

- `/books/` - List all books
- `/book/<id>/` - List chapters in a book
- `/read/<segment_id>/` - Read a specific segment with TTS
- `/api/tts/` - API endpoint for TTS data

## Technical Details

### TTS Implementation
- Uses **Web Speech API** (SpeechSynthesisUtterance)
- No server-side audio processing required
- Works in all modern browsers
- Falls back gracefully if no Chinese voice available
- Adjustable speech rate (default: 0.8 for learning)

### Browser Support
- ✅ Chrome/Edge (best Chinese voice support)
- ✅ Safari (iOS/macOS)
- ✅ Firefox
- ⚠️ Some older browsers may have limited voice options

### Responsive Design
- Mobile-friendly layout
- Touch-optimized buttons
- Keyboard shortcuts for desktop
- Adaptive font sizes

## Tips for Content Creation

1. **Consistency**: Keep pinyin formatting consistent (tone marks, spacing)
2. **Segment Length**: Keep segments short (1-3 sentences) for better learning
3. **Key Words**: Link relevant vocabulary to help students
4. **Progressive Difficulty**: Start simple, increase complexity gradually
5. **Context**: Provide enough context in translations

## Future Enhancements

Potential improvements:
- [ ] Pre-generated audio files for better quality
- [ ] Multiple voice options
- [ ] Speed control slider
- [ ] Recording feature for pronunciation practice
- [ ] Progress tracking per segment
- [ ] Quiz mode based on reading passages
- [ ] PDF export of chapters
- [ ] Bookmarking favorite segments

## Troubleshooting

### TTS Not Working?
1. Check browser compatibility
2. Ensure volume is not muted
3. Try a different browser (Chrome recommended)
4. Check if voices are loaded (`speechSynthesis.getVoices()`)

### Missing Content?
- Add books/chapters/segments through Django Admin
- Use the fixtures or import scripts for bulk data

### Navigation Issues?
- Ensure segments have sequential order numbers
- Check that chapters are linked to correct books
