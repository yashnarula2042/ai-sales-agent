import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-1.5-pro'
        else:
            self.client = None
            
        self.persona = f"""
        You are a world-class, high-end Sales Strategist for a premium Website Design & Development agency.
        Your expertise is in identifying conversion bottlenecks and presenting website redesigns as high-ROI business investments.
        Your writing style is sophisticated, concise, and highly personalized. 
        You avoid sales cliches and focus on being a "trusted advisor" who has done their research.
        
        Recent Success Story: You recently designed and developed https://www.firdausawadhikitchen.com/, 
        which is a prime example of your work in combining high-end aesthetics with functional performance.
        
        Meeting Link: The user's booking link is {os.getenv("MEETING_LINK")}.
        """

    def generate_email(self, lead_name, company, website):
        meeting_link = os.getenv("MEETING_LINK", "https://calendar.app.google/ifrAsBGRXb8oHKY3A")
        if not self.client:
            print("Gemini API key not found. Using fallback.")
            return self._fallback_email(lead_name, company)

        prompt = f"""
        Role: {self.persona}
        
        Lead Details:
        - Lead Name: {lead_name}
        - Company Name: {company}
        - Current Website: {website}
        - Booking Link: {meeting_link}
        
        Objective:
        Write a hyper-personalized, one-on-one cold email that feels like it came from a human, not a bot.
        
        Guidelines:
        1. Open with a specific observation about {company}. 
        2. Briefly mention a conversion "leak" or design issue businesses in their niche often face.
        3. Position a redesign as a way to "capture lost revenue" rather than just looking "prettier."
        4. The CTA: Offer a "zero-commitment audit" or a "quick visual concept."
        5. Provide your Booking Link ({meeting_link}) as an easy way for them to pick a time if they're interested. Example: "Feel free to grab a time on my calendar here: {meeting_link}"
        6. SOCIAL PROOF (ENDING): After the CTA and before the sign-off, you MUST add exactly this phrase: "Here is a website that I recently created for one of my client: https://www.firdausawadhikitchen.com/"
        7. Style: No fluff. No emojis in the subject. Short paragraphs (1-2 lines max).
        
        IMPORTANT: Your response MUST follow this exact structure:
        [SUBJECT]
        Put the subject line here (make it short and intriguing, no emojis).
        [BODY]
        Put the email body here. Use [Your Name] as the sign-off placeholder.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating AI email with Gemini: {e}")
            return self._fallback_email(lead_name, company)

    def _fallback_email(self, lead_name, company):
        meeting_link = os.getenv("MEETING_LINK", "https://calendar.app.google/ifrAsBGRXb8oHKY3A")
        return f"""
[SUBJECT]
Question about {company}'s website
[BODY]
Hi {lead_name},

I recently came across {company} and noticed a few areas where your website might be losing potential customers.

I'd love to send over a 2-minute audit of your homepage's conversion leaks. Should I send it over?

If you'd rather walk through it together, feel free to pick a time here: {meeting_link}

Here is a website that I recently created for one of my client: https://www.firdausawadhikitchen.com/

Best regards,
[Your Name]
"""
