import pandas as pd
from .database import get_session, Lead, LeadStatus, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file logging for debugging
fh = logging.FileHandler('debug_import.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class LeadManager:
    def __init__(self):
        init_db()

    def import_from_csv(self, file_path):
        """Imports leads from a CSV file with robust detection."""
        try:
            import chardet
            
            # 1. Detect encoding
            with open(file_path, 'rb') as f:
                rawdata = f.read(10000)
                result = chardet.detect(rawdata)
                encoding = result['encoding'] or 'utf-8'
                logger.info(f"Detected encoding: {encoding}")

            # 2. Try loading with different separators
            df = None
            for sep in [',', ';', '\t', '|']:
                try:
                    # Reset pointer and try reading
                    test_df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=5)
                    # If it successfully read and didn't result in a single column with the separator in it
                    if len(test_df.columns) > 1 or (len(test_df.columns) == 1 and sep not in str(test_df.iloc[0,0])):
                        df = pd.read_csv(file_path, sep=sep, encoding=encoding)
                        logger.info(f"Successfully parsed CSV with separator: '{sep}'")
                        break
                except:
                    continue
            
            if df is None:
                # Last ditch effort with default pandas settings
                df = pd.read_csv(file_path, encoding=encoding)

            # Fuzzy Match Columns
            cols = {str(c).lower().strip(): c for c in df.columns}
            logger.info(f"Columns detected: {list(cols.keys())}")
            
            def find_col(possible_names):
                for name in possible_names:
                    for col_lower in cols:
                        if name in col_lower:
                            return cols[col_lower]
                return None

            email_col = find_col(['email', 'mail', 'contact'])
            name_col = find_col(['name', 'owner', 'person', 'contact'])
            company_col = find_col(['company', 'business', 'firm', 'organization'])
            website_col = find_col(['website', 'url', 'site', 'link'])

            if not email_col:
                available = ", ".join([str(c) for c in df.columns])
                logger.error(f"Required 'email' column missing. Found columns: {available}")
                raise ValueError(f"Could not find an 'Email' column. Found: {available}. Please ensure your CSV has an 'email' column.")

            session = get_session()
            new_leads_count = 0
            duplicate_count = 0
            invalid_count = 0
            total_rows = len(df)
            
            logger.info(f"Processing {total_rows} rows from CSV...")
            if total_rows > 0:
                logger.info(f"Sample row 0: {df.iloc[0].to_dict()}")

            for i, row in df.iterrows():
                try:
                    val = row[email_col]
                    if pd.isna(val): 
                        invalid_count += 1
                        continue
                    email = str(val).strip()
                    if not email or "@" not in email:
                        logger.warning(f"Row {i}: Invalid email format '{email}'")
                        invalid_count += 1
                        continue

                    # Check if lead already exists
                    existing = session.query(Lead).filter_by(email=email).first()
                    if not existing:
                        lead = Lead(
                            name=str(row[name_col]) if name_col and not pd.isna(row[name_col]) else 'Business Owner',
                            email=email,
                            company=str(row[company_col]) if company_col and not pd.isna(row[company_col]) else 'Unknown',
                            website=str(row[website_col]) if website_col and not pd.isna(row[website_col]) else 'Unknown',
                            status=LeadStatus.PENDING
                        )
                        session.add(lead)
                        new_leads_count += 1
                    else:
                        duplicate_count += 1
                except Exception as row_err:
                    logger.warning(f"Row {i}: Skipping due to error: {row_err}")
                    invalid_count += 1
                    continue
            
            session.commit()
            session.close()
            
            status_msg = f"Import Result: {new_leads_count} new leads added. {duplicate_count} duplicates skipped. {invalid_count} invalid rows skipped."
            logger.info(status_msg)
            return status_msg
        except Exception as e:
            logger.error(f"Error importing CSV: {str(e)}")
            raise ValueError(f"Import failed: {str(e)}")

    def add_single_lead(self, name, email, company='Unknown', website='Unknown'):
        """Adds a single lead to the database with duplicate checking."""
        session = get_session()
        try:
            email = email.strip()
            if not email or "@" not in email:
                raise ValueError("Invalid email format")

            existing = session.query(Lead).filter_by(email=email).first()
            if existing:
                return False, f"Lead with email {email} already exists."

            lead = Lead(
                name=name if name else 'Business Owner',
                email=email,
                company=company if company else 'Unknown',
                website=website if website else 'Unknown',
                status=LeadStatus.PENDING
            )
            session.add(lead)
            session.commit()
            return True, "Lead added successfully."
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding single lead: {e}")
            raise e
        finally:
            session.close()

    def get_pending_leads(self):
        session = get_session()
        try:
            leads = session.query(Lead).filter_by(status=LeadStatus.PENDING).all()
            # Explicitly load data and detach from session so they can be used in other threads
            session.expunge_all()
            return leads
        finally:
            session.close()

    def update_lead_status(self, lead_id, status, email_content=None, error_message=None):
        session = get_session()
        lead = session.query(Lead).filter_by(id=lead_id).first()
        if lead:
            lead.status = status
            if email_content:
                lead.personalized_email = email_content
            if error_message:
                lead.error_message = error_message
            session.commit()
        session.close()

    def clear_all_leads(self):
        """Deletes all leads from the database."""
        session = get_session()
        try:
            session.query(Lead).delete()
            session.commit()
            logger.info("All leads cleared from the database.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing leads: {e}")
            raise e
        finally:
            session.close()

    def reset_lead_statuses(self):
        """Resets all SENT and FAILED leads to PENDING."""
        session = get_session()
        try:
            leads = session.query(Lead).filter(Lead.status.in_([LeadStatus.SENT, LeadStatus.FAILED])).all()
            for lead in leads:
                lead.status = LeadStatus.PENDING
                lead.error_message = None
                lead.personalized_email = None
            session.commit()
            logger.info(f"Reset {len(leads)} leads to pending.")
            return len(leads)
        except Exception as e:
            session.rollback()
            logger.error(f"Error resetting leads: {e}")
            raise e
        finally:
            session.close()
