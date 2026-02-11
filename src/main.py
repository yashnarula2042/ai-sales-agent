import time
import logging
from .lead_manager import LeadManager, LeadStatus
from .ai_agent import AIAgent
from .email_sender import EmailSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesAgentOrchestrator:
    def __init__(self):
        self.lead_manager = LeadManager()
        self.ai_agent = AIAgent()
        self.email_sender = EmailSender()
        self._stop_requested = False
        self.is_running = False
        self.is_paused = False

    def run_automation_cycle(self, limit=1000):
        """Processes a batch of pending leads."""
        if self.is_running:
            logger.warning("Automation already running.")
            return

        self.is_running = True
        self._stop_requested = False
        self.is_paused = False
        
        try:
            pending_leads = self.lead_manager.get_pending_leads()
            if not pending_leads:
                logger.info("No pending leads found.")
                return

            logger.info(f"Processing up to {limit} leads...")
            count = 0
            for lead in pending_leads:
                if count >= limit: break
                if self._stop_requested:
                    logger.info("Automation stop requested. Exiting loop.")
                    break
                
                # Manual Pause check
                while self.is_paused and not self._stop_requested:
                    time.sleep(1)
                
                if self._stop_requested: break

                try:
                    # 1. Generate Voice/Content
                    logger.info(f"Generating personalized email for {lead.email}...")
                    email_output = self.ai_agent.generate_email(lead.name, lead.company, lead.website)
                    
                    # Clean up potential Markdown code blocks from AI
                    clean_output = email_output.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
                    
                    # Split subject and body using new [SUBJECT] and [BODY] tags
                    import os
                    sender_name = os.getenv("SENDER_NAME", "Yash Narula")
                    
                    subject = f"Question about {lead.company}"
                    body = clean_output

                    if "[SUBJECT]" in clean_output and "[BODY]" in clean_output:
                        try:
                            # Extract SUBJECT section
                            subject_part = clean_output.split("[SUBJECT]")[1].split("[BODY]")[0].strip()
                            # Extract BODY section
                            body_part = clean_output.split("[BODY]")[1].split("[SUBJECT]")[0] if "[SUBJECT]" in clean_output.split("[BODY]")[1] else clean_output.split("[BODY]")[1]
                            
                            subject = subject_part.strip()
                            body = body_part.strip()
                        except Exception as parse_err:
                            logger.warning(f"Parse error for AI output: {parse_err}. Falling back to default split.")
                            if "[BODY]" in clean_output:
                                parts = clean_output.split("[BODY]")
                                subject = parts[0].replace("[SUBJECT]", "").strip()
                                body = parts[1].strip()

                    # Final cleaning of any leftover labels
                    subject = subject.replace("Subject:", "").replace("SUBJECT:", "").replace("subject:", "").strip()
                    subject = subject.replace("[SUBJECT]", "").replace("[subject]", "").strip()
                    # Remove any leading/trailing quotes that AI sometimes adds
                    subject = subject.strip('"').strip("'").strip()
                    
                    body = body.replace("Body:", "").replace("BODY:", "").replace("body:", "").strip()
                    body = body.replace("[BODY]", "").replace("[body]", "").strip()
                    
                    # Replace [Your Name] placeholder
                    body = body.replace("[Your Name]", sender_name)
                    body = body.replace("[your name]", sender_name)
                    body = body.replace("Your Name", sender_name)
                    
                    # 2. Update status to AI_GENERATED
                    self.lead_manager.update_lead_status(lead.id, LeadStatus.AI_GENERATED, f"Subject: {subject}\n\n{body}")

                    # 3. Send Email
                    logger.info(f"Sending email to {lead.email} with subject: {subject}...")
                    success, message = self.email_sender.send_email(lead.email, subject, body)
                    
                    if success:
                        self.lead_manager.update_lead_status(lead.id, LeadStatus.SENT)
                    else:
                        self.lead_manager.update_lead_status(lead.id, LeadStatus.FAILED, error_message=message)
                    
                    count += 1
                    # Rate limiting (wait 30 seconds between emails)
                    if count < len(pending_leads) and count < limit:
                        logger.info("Waiting 30 seconds before next lead...")
                        # Nested check for pause during wait
                        for _ in range(30):
                            if self._stop_requested: break
                            while self.is_paused and not self._stop_requested:
                                time.sleep(1)
                            time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing lead {lead.email}: {e}")
                    try:
                        self.lead_manager.update_lead_status(lead.id, LeadStatus.FAILED)
                    except: pass
        
        finally:
            self.is_running = False
            logger.info("Automation cycle finished.")

    def stop(self):
        """Signals the orchestrator to stop processing."""
        self._stop_requested = True
        self.is_paused = False # Unpause to allow exit
        logger.info("Stop signal received.")

    def pause(self):
        """Signals the orchestrator to pause processing."""
        self.is_paused = True
        logger.info("Automation paused.")

    def resume(self):
        """Signals the orchestrator to resume processing."""
        self.is_paused = False
        logger.info("Automation resumed.")

if __name__ == "__main__":
    orchestrator = SalesAgentOrchestrator()
    orchestrator.run_automation_cycle()
