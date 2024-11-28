import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.tfidf = TfidfVectorizer()

    def clean_text(self, text):
        """Basic text cleaning"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def remove_stopwords(self, text):
        """Remove stopwords from text"""
        words = word_tokenize(text)
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)

    def preprocess_text(self, text):
        """Complete text preprocessing pipeline"""
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        return text

    def deduplicate_texts(self, texts):
        """Remove duplicate texts using TF-IDF similarity"""
        if not texts:
            return []

        # Convert texts to TF-IDF vectors
        tfidf_matrix = self.tfidf.fit_transform(texts)
        
        # Calculate pairwise similarities
        unique_indices = []
        seen = set()
        
        for i in range(len(texts)):
            if i in seen:
                continue
                
            unique_indices.append(i)
            current_vector = tfidf_matrix[i]
            
            # Find similar texts
            for j in range(i + 1, len(texts)):
                if j in seen:
                    continue
                    
                similarity = (current_vector * tfidf_matrix[j].T).toarray()[0][0]
                if similarity > 0.9:  # Threshold for considering texts as duplicates
                    seen.add(j)
                    
            seen.add(i)
        
        return [texts[i] for i in unique_indices]
