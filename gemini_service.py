import google.generativeai as genai
import os
from typing import Dict, List, Tuple

class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def get_certification_domains(self, certification: str) -> List[str]:
        """Get domains for a specific certification."""
        prompt = f"""
        List the main domains/topics for the {certification} certification.
        Return only the domain names as a simple list without any additional text or numbers.
        These should be the actual exam domains from the official certification guide.
        """
        try:
            response = self.model.generate_content(prompt)
            domains = [domain.strip() for domain in response.text.split('\n') if domain.strip()]
            return domains
        except Exception as e:
            print(f"Error fetching domains: {str(e)}")
            return []

    def generate_flashcards(self, certification: str, domain: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """Generate flashcards for a specific certification domain."""
        prompt = f"""
        Create {num_cards} flash cards for the {domain} domain of {certification} certification.
        Each card should have a question and answer format.
        Focus on important concepts and key points that are likely to appear in the actual certification exam.
        Format each card as:
        Q: [Question]
        A: [Answer]

        Make sure each question-answer pair is separated by a newline.
        """
        try:
            response = self.model.generate_content(prompt)
            cards = []
            current_card = {}
            
            for line in response.text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Q:'):
                    if current_card:
                        cards.append(current_card)
                        current_card = {}
                    current_card['question'] = line[2:].strip()
                elif line.startswith('A:'):
                    current_card['answer'] = line[2:].strip()
            
            if current_card:
                cards.append(current_card)
                
            return cards[:num_cards]  # Ensure we only return the requested number of cards
        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return []

    def get_certification_content(self, certification: str) -> Dict[str, List[Dict[str, str]]]:
        """Get complete content for a certification including domains and flashcards."""
        domains = self.get_certification_domains(certification)
        content = {}
        
        for domain in domains:
            cards = self.generate_flashcards(certification, domain)
            if cards:  # Only add domain if we successfully generated cards
                content[domain] = cards
                
        return content