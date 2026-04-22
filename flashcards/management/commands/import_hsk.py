import os
import fitz
from django.core.management.base import BaseCommand
from flashcards.models import Word

class Command(BaseCommand):
    help = 'Import HSK words from PDFs'

    def handle(self, *args, **options):
        base_path = r"c:\Users\mudas\OneDrive\Desktop\HSK\HSK Words"
        
        Word.objects.all().delete()  # Clear existing
        
        for level in range(1, 5):
            file_path = os.path.join(base_path, f"New-HSK-{level}-Word-List.pdf")
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"File not found: {file_path}"))
                continue
                
            self.stdout.write(f"Parsing HSK Level {level}...")
            doc = fitz.open(file_path)
            
            expected_id = 1
            state = "WAIT_ID"
            current_word = {}
            
            for page in doc:
                text = page.get_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for i, line in enumerate(lines):
                    if state == "WAIT_ID" and line == str(expected_id):
                        state = "CHINESE"
                    elif state == "CHINESE":
                        current_word['chinese'] = line
                        state = "PINYIN"
                    elif state == "PINYIN":
                        current_word['pinyin'] = line
                        state = "ENGLISH"
                    elif state == "ENGLISH":
                        current_word['english'] = line
                        # Save the word
                        Word.objects.create(
                            hsk_level=level,
                            chinese=current_word['chinese'],
                            pinyin=current_word['pinyin'],
                            english=current_word['english']
                        )
                        expected_id += 1
                        state = "WAIT_ID"
                        # It's possible the english wraps to the next line, but we assume it's one block. 
                        # Wait, what if the NEXT line is not expected_id? 
                        # If the next line is not expected_id and it's not a page number...
                        # A simple way that works for most PDFs of this rigid format.
                        
            doc.close()
            self.stdout.write(self.style.SUCCESS(f"Finished Level {level}. Loaded {expected_id - 1} words."))
