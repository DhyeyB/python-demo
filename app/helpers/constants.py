"""All the constants which is used in project is defined in this file."""
import enum


class EnumBase(enum.Enum):
    """Base class for all enums with common method"""

    @classmethod
    def get_name(cls, status):
        """Returns the name of each item in enum"""
        for name, member in cls.__members__.items():
            if member.value == status:
                return str(member.value)
        return None


class Methods(enum.Enum):
    """ http methods used"""
    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class HttpStatusCode(enum.Enum):
    """Enum for storing different http status code."""
    OK = '200'
    BAD_REQUEST = '400'
    UNAUTHORIZED = '401'
    FORBIDDEN = '403'
    NOT_FOUND = '404'
    INTERNAL_SERVER_ERROR = '500'
    TOO_MANY_REQUESTS = '429'

    @classmethod
    def get_name(cls, status):
        """This method returns key name of enum from value."""
        if status == cls.OK.value:
            return 200
        elif status == cls.BAD_REQUEST.value:
            return 400
        elif status == cls.UNAUTHORIZED.value:
            return 401
        elif status == cls.FORBIDDEN.value:
            return 403
        elif status == cls.INTERNAL_SERVER_ERROR.value:
            return 500
        else:
            return None


class ResponseMessageKeys(enum.Enum):
    """API response messages for various purposes"""

    INVALID_TOKEN = 'Invalid Token.'
    TOKEN_EXPIRED = 'Token Expired, Try sign in again.'
    NOT_ALLOWED = 'User is not allowed for this request.'
    ENTER_CORRECT_INPUT = 'Enter correct input.'
    LOGIN_SUCCESSFULLY = 'Hi {0}, great to see you!'
    INVALID_EMAIL_FORMAT = 'Invalid email format.'
    INVALID_MOBILE_NUMBER_FORMAT = 'Mobile number should be numeric and must be of 10 digits.'
    LOGIN_FAILED = 'Login Failed.'
    LOGOUT_SUCCESSFULLY = 'Logout Successfully.'
    ADMIN_USER_ADDED_SUCCESSFULLY = 'Admin user added successfully.'
    RECORD_ADDED_SUCCESSFULLY = 'Record Added Successfully.'
    RECORD_UPDATED_SUCCESSFULLY = 'Record updated Successfully.'
    RECORD_DELETED_SUCCESSFULLY = 'Record Deleted Successfully.'
    SUCCESS = 'Details Fetched Successfully.'
    REGISTER_SUCCESSFULLY = 'User Registered Successfully.'
    ADMIN_REGISTER_SUCCESSFULLY = 'Admin Registered Successfully.'
    UPDATED_SUCCESSFULLY = 'User Updated Successfully.'
    DELETED_SUCCESSFULLY = 'User Deleted Successfully.'
    USER_VERIFICATION_SUCCESS = 'User Verified Successfully.'
    USER_VERIFICATION_FAILED = 'User Verification Failed.'
    FAILED = 'Something went wrong.'
    COGNITO_USER_CREATION_FAILED = 'Cognito User Creation Failed.'
    USER_CREATION_FAILED = 'User Creation Failed.'
    INVALID_PASSWORD = 'Invalid password.'
    ACCESS_DENIED = 'Access Denied.'
    USER_NOT_EXIST = 'Entered Email ID is not registered with us.'
    USER_NOT_CONFIRMED = 'User is not confirmed in Cognito.'
    USER_ALREADY_CONFIRMED = 'Entered Email ID is already confirmed.'
    USER_DETAILS_NOT_FOUND = 'User Details Not Found.'
    INVALID_VERIFICATION_CONFIRMED = 'Invalid Verification Code.'
    EMAIL_ALREADY_EXIST = 'User with {} email already exist.'
    MOBILE_ALREADY_EXIST = 'User with same mobile number already exist.'
    EMAIL_DETAILS_NOT_FOUND = 'Entered Email ID is not registered with us.'
    MESSAGE_RECEIVED_SUCCESSFULLY = 'Your message has been received.'
    CONTACT_US_REQUEST_NOT_FOUND = 'Contact Us Request not found.'
    USER_NOT_FOUND = 'User not found.'
    ACCOUNT_NOT_FOUND = 'Account not found.'
    PLAN_NOT_FOUND = 'Plan not found.'
    SUBSCRIPTION_NOT_FOUND = 'Subscription not found.'
    CONTRACT_SIGNEE_NOT_FOUND = 'Contract signee not found.'
    UNKNOWN_ERROR = 'Unknown error occurred.'
    VERIFICATION_CODE_RESEND_SUCCESS = 'Verification code resent successfully.'
    PAYMENT_FAILED = 'Payment failed.'
    PAYMENT_SUCCESSFULLY = 'Payment successfully.'
    USER_DOES_NOT_HAVE_ACTIVE_PLAN = 'User does not have active plan.'
    CLIENT_CREATED_SUCCESSFULLY = 'Client(s) created successfully.'
    CLIENT_DATA_UPDATED_SUCCESSFULLY = 'Client data updated successfully.'
    CLIENT_NOT_FOUND = 'Client not found.'
    CLIENT_ALREADY_EXISTS = 'Client {0} already exists.'
    SIGNEES_CREATED_SUCCESSFULLY = 'Signees created successfully.'
    SIGNEE_NOT_FOUND = 'Signee not found.'
    SIGNEE_DATA_UPDATED_SUCCESSFULLY = 'Signee(s) data updated successfully.'
    SIGNEE_EMAIL_ALREADY_EXISTS = 'Signee with {0} email already exists.'
    INVALID_FILE_TYPE = 'Invalid file type.'
    USER_DOES_BELONG_TO_GIVEN_ACCOUNT = 'User does not belong to given account.'
    SEND_USER_INVITE_FAILED = 'Send user invite failed.'
    SEND_USER_INVITE_SUCCESS = 'Send user invite success.'
    RESEND_USER_INVITE_FAILED = 'Resend user invite failed.'
    RESEND_USER_INVITE_SUCCESS = 'Resend user invite success.'
    INVITE_TOKEN_VERIFIED_SUCCESSFULLY = 'Invite token verified successfully.'
    USER_ALREADY_ACCEPTED_INVITATION = 'User has already accepted invitation.'
    USER_INVITE_NOT_FOUND = 'User invite not found.'
    INVITE_ACCEPTED_SUCCESSFULLY = 'Invite accepted successfully.'
    INVITE_ALREADY_ACCEPTED = 'Invite already accepted.'
    USER_ACCOUNT_NOT_SETUP = 'User account not setup.'
    CONTRACT_CREATED_SUCCESSFULLY = 'Contract created successfully.'
    CONTRACT_IS_SENT = 'Contract is sent to signee(s).'
    CONTRACT_STATUS_SIGNED = 'Contract status updated to Signed.'
    CONTRACT_IS_CANCELLED = 'Contract is cancelled.'
    INCORRECT_CONTRACT_STATUS = 'Incorrect contract status.'
    CONTRACT_DATA_UPDATED_SUCCESSFULLY = 'Contract data updated successfully.'
    CONTRACT_NOT_FOUND = 'Contract not found.'
    STATUS_UPDATED_SUCCESSFULLY = 'Status updated successfully.'
    LOG_IS_ADDED_SUCCESSFULLY = 'Log is added successfully.'
    CONTRACT_TOKEN_VERIFIED_SUCCESSFULLY = 'Contract token verified successfully.'
    USER_ALREADY_EXISTS = 'User already exists.'
    EMAIL_UPDATE_UNSUCCESSFUL = 'Email update unsuccessful.'
    EMAIL_UPDATED_SUCCESSFULLY = 'Email updated successfully.'
    VERIFICATION_MAIL_SENT = 'Verification mail sent'
    BRANDING_DETAILS_NOT_FOUND = 'Branding details not found.'
    FILE_NOT_FOUND = 'File not found.'
    INVALID_IMAGE_FORMAT = 'Invalid image format.'
    IMAGE_STORED_SUCCESSFULLY = 'Image stored successfully.'
    FOLDER_ALREADY_EXISTS = 'Folder {0} already exists.'
    FOLDER_NOT_FOUND = 'Folder not found.'
    SIGEE_ALREADY_HAVE_CONTRACT_ASCCOCIATED_AND_CANT_BE_DELETED = 'Data updated successfully {} cannot be deleted due to an associated contract'
    FOLDER_HAVE_CONTRACT_ASCCOCIATED_AND_CANT_BE_DELETED = 'Folder have contract associated and cannot be deleted'
    INVALID_FOLDER_NAME = 'Folder name can only contain alphabets, numbers, dashes, and underscores, and no other special characters are allowed.'
    ACCOUNT_DELETION_REQUEST_ADDED_SUCCESSFULLY = 'Account deletion request added successfully.'
    EMAIL_TEMPLATE_NOT_FOUND = 'Email template not found.'
    USER_INVITE_DELETED_SUCCESSFULLY = 'User Invite deleted successfully.'
    DOWNLOAD_AS_PDF_SUCCESSFUL = 'Download as pdf successful.'


class DataLevel(EnumBase):
    """Data level for serializer status enum"""
    INFO = 'INFO'
    DETAIL = 'DETAIL'


class ValidationMessages(enum.Enum):
    """ Validation messages for different fields."""
    EMAIL_REQUIRED = 'Please Enter Email ID.'
    FIRST_NAME_REQUIRED = 'First name is mandatory to add.'
    LAST_NAME_REQUIRED = 'Last name is mandatory to add.'
    ADDRESS_REQUIRED = 'Address is mandatory to add.'
    PHONE_REQUIRED = 'Phone number is mandatory to add.'
    NAME_REQUIRED = 'Name is mandatory to add.'
    COMPANY_NAME_REQUIRED = 'Company name is mandatory to add.'
    LEGAL_NAME_REQUIRED = 'Legal name is mandatory to add.'
    DISPLAY_NAME_REQUIRED = 'Display name is mandatory to add.'
    COMPANY_SIZE_REQUIRED = 'Company size is mandatory to add.'
    MESSAGE_REQUIRED = 'Message is mandatory to add.'
    FULL_NAME_REQUIRED = 'Full name is mandatory to add.'
    CLIENT_UUID_REQUIRED = 'Client is mandatory to add.'
    SIGNING_SEQUENCE_REQUIRED = 'Signing sequence is mandatory to add.'
    PURPOSE_REQUIRED = 'Purpose is mandatory to add.'
    SIGNEES_REQUIRED = 'Signee(s) is/are mandatory to select.'
    BRIEF_REQUIRED = 'Brief is mandatory to add.'
    SERVICE_NAME_REQUIRED = 'Service Name is mandatory to add.'
    DURATION_REQUIRED = 'Duration is mandatory to add.'
    AMOUNT_REQUIRED = 'Amount is mandatory to add.'
    CONTENT_REQUIRED = 'Content is required.'
    QUERY_REQUIRED = 'Query is required.'
    COVER_PAGE_REQUIRED = 'Cover Page is required.'
    FOLDER_NAME_REQUIRED = 'Folder Name is mandatory to add.'
    FOLDER_IS_REQUIRED = 'Folder is required.'
    EMAIL_SUBJECT_IS_REQUIRED = 'Email Subject is required.'
    EMAIL_BODY_IS_REQUIRED = 'Email Body is required.'


class QueueName:
    """redis queue scheduler names"""
    SEND_MAIL = 'SEND_MAIL'
    REMINDER_MAIL = 'REMINDER_MAIL'
    DELETE_ACCOUNT = 'DELETE_ACCOUNT'
    CHECK_SUBSCRIPTION_EXPIRY = 'CHECK_SUBSCRIPTION_EXPIRY'


class SortingOrder(EnumBase):
    """Enum for storing sorting parameters value."""
    ASC = 'asc'
    DESC = 'desc'


class SortingParams(EnumBase):
    """Enum for storing transactions."""
    AMOUNT = 'AMOUNT'
    DATE = 'DATE'
    NAME = 'NAME'
    TITLE = 'TITLE'


class DatabaseAction(enum.Enum):
    """
        Database operation names.
    """
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    READ = 'read'


class UserType(enum.Enum):
    """User Types"""

    SUPER_ADMIN = 'super_admin'
    PRIMARY_USER = 'primary_user'
    SECONDARY_USER = 'secondary_user'


class SubscriptionStatus(enum.Enum):
    """Status of a subscription"""

    INACTIVE = 'inactive'
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'


class PlanPeriod(enum.Enum):
    YEARLY = 'year'
    MONTHLY = 'month'


class DurationType(enum.Enum):
    """Duration period enum for Contract field - Duration"""
    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'


class PaymentFrequency(enum.Enum):
    """Payment Frequency enum for Contract field - Payment Frequency"""
    ONE_TIME = 'one time'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


SupportedExcelTypes = {  # Contains all the supported Excel types.
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}


class SubscriptionDays(enum.Enum):

    TRIAL_PERIOD_DAYS = 15


class ErrorCode(enum.Enum):

    SUBSCRIPTION_NOT_FOUND = 'SUBSCRIPTION_NOT_FOUND'
    ACCOUNT_NOT_SETUP = 'ACCOUNT_NOT_SETUP'
    EMAIL_ALREADY_EXISTS = 'EMAIL_ALREADY_EXISTS'
    EMAIL_UPDATE_UNSUCCESSFUL = 'EMAIL_UPDATE_UNSUCCESSFUL'


class EmailSubject(enum.Enum):
    """Emails subject's texts"""
    SUBSCRIPTION_CREATED_WITH_FREE_TRIAL = 'Your VirtuSign Free Trial Has Begun!'
    SUBSCRIPTION_CREATED_WITHOUT_FREE_TRIAL = 'Your VirtuSign Subscription Has Begun!'
    USER_INVITE = 'Invitation to Join VirtuSign!'
    WELCOME = 'Welcome to VirtuSign - Your AI Powered Digital Signature Solution'
    CONTACT_US_SUBMISSION = 'Virtu Sign - New Contact Us Submission Received - Action Required'
    NEW_CLIENT_ADDED = 'New Client Added to Your Account'
    SEND_CONTRACT_TO_SIGNEE = 'Document for E-Signature - Action Required'
    CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE = 'Document Signature Confirmation: Status Complete'
    CONTRACT_SIGNED_BY_ALL_SIGNEE = 'All Signees Have Signed the Contract'
    CONTRACT_CANCELLED = 'Cancellation of E-Contract'
    SEND_REMINDER_TO_SIGNEE = 'Reminder for Electronic Signature'
    ACCOUNT_DELETION_REQUEST_INTIATED = 'Account Deletion Request Initiated'
    ACCOUNT_DELETION_CONFIRMATION = 'Account Deletion Confirmation'


class EmailTypes(enum.Enum):
    """Enum for storing different Email Types."""
    INVITE = 'INVITE'
    SUBSCRIPTION_CREATED_WITH_FREE_TRIAL = 'SUBSCRIPTION_CREATED_WITH_FREE_TRIAL'
    SUBSCRIPTION_CREATED_WITHOUT_FREE_TRIAL = 'SUBSCRIPTION_CREATED_WITHOUT_FREE_TRIAL'
    WELCOME = 'WELCOME'
    CONTACT_US_SUBMISSION = 'CONTACT_US_SUBMISSION'
    CLIENT_ADDED = 'CLIENT_ADDED'
    SEND_CONTRACT_TO_SIGNEE = 'SEND_CONTRACT_TO_SIGNEE'
    CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE = 'CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE'
    UPDATE_CONTRACT_AUTHOR_WHEN_CONTRACT_SIGNED_BY_ALL_SIGNEE = 'UPDATE_CONTRACT_AUTHOR_WHEN_CONTRACT_SIGNED_BY_ALL_SIGNEE'
    CONTRACT_CANCELLED = 'CONTRACT_CANCELLED'
    SEND_REMINDER_TO_SIGNEE = 'SEND_REMINDER_TO_SIGNEE'
    ACCOUNT_DELETION_REQUEST_INTIATED = 'ACCOUNT_DELETION_REQUEST_INTIATED'
    ACCOUNT_DELETION_CONFIRMATION = 'ACCOUNT_DELETION_CONFIRMATION'

    @staticmethod
    def get_email_template_name_by_email_type(email_type: str):
        """Returns the email template name by email type"""
        if email_type == EmailTypes.SEND_CONTRACT_TO_SIGNEE.value:
            return 'Send Contract To Signee'
        elif email_type == EmailTypes.CONTRACT_CANCELLED.value:
            return 'Contract Cancelled'
        elif email_type == EmailTypes.CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE.value:
            return 'Contract Signing Signee Status Complete'
        elif email_type == EmailTypes.SEND_REMINDER_TO_SIGNEE.value:
            return 'Send Reminder To Signee'
        else:
            return 'Default Email Template Name'


class UserInviteStatusTypes(enum.Enum):
    """Enum for storing different Email Types."""
    PENDING = 'pending'
    ACCEPTED = 'accepted'


class ContractStatus(enum.Enum):
    """Enum for storing Contract status"""
    DRAFT = 'draft'
    SENT_FOR_SIGNING = 'sent_for_signing'
    SIGNED = 'signed'
    CANCELLED = 'cancelled'


class ContractMailStatus(enum.Enum):
    """Enum for listing status of mail to signee for contract"""
    NOT_SENT = 'not_sent'
    PENDING = 'pending'
    SIGNED = 'signed'


class SignatureTypes(enum.Enum):
    """Enum for signature type"""
    TEXT = 'text'
    SVG = 'svg'
    IMAGE = 'image'


class TimeInSeconds(EnumBase):
    """Enum that will return time in seconds from different keys. (ex.Five_MIN=300)"""
    FIVE_MIN = 300
    THIRTY_MIN = 1800
    SIXTY_MIN = 3600
    TWENTY_FOUR_HOUR = 86400
    TWO_DAYS = 172800
    ONE_MONTH = 2592000


SupportedImageTypes = {  # Contains all the supported image types.
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'jpg': 'image/jpg'
}


DEFAULT_PRE_DELETION_PERIOD_IN_DAYS = 30

DEFAULT_SECTIONS = ['Definitions and Interpretation', 'Liability and Indemnification', 'Parties to the Agreement',
                    'Recitals', 'Rights and Obligations', 'Termination and Consequences.', 'Terms and Conditions']
DEFAULT_SECTION_DICT = {
    'Definitions and Interpretation': "In this Agreement, unless the context otherwise requires, the following words and phrases shall have the following meanings:<br><br>1. \"Agreement\" refers to the agreement established between Party A and Party B which encompasses all written terms, conditions and provisions provided herein.<br><br>2. \"Business Day\" shall mean any day excluding Saturday, Sunday and public holidays in England.<br><br>3. \"Confidential Information\" includes any information disclosed by either party to the other, either directly or indirectly in writing, orally or by inspection of tangible objects, which is of a confidential nature.<br><br>4. \"Effective Date\" refers to the date on which the terms and conditions of this Agreement are accepted by both parties.<br><br>5. \"Intellectual Property Rights\" means all patents, rights to inventions, copyright and related rights, trademarks, business names and domain names, rights in get-up and trade dress, goodwill and the right to sue for passing off, rights in designs, database rights, rights to use, and protect the confidentiality of, confidential information (including know-how), and all other intellectual property rights, in each case whether registered or unregistered and including all applications and rights to apply for and be granted, renewals or extensions of, and rights to claim priority from, such rights and all similar or equivalent rights or forms of protection which subsist or will subsist now or in the future in any part of the world.<br><br>6. \"Party\", \"Parties\" refers to Party A and Party B either collectively or individually.<br><br>7. \"Services\" refers to the services to be provided by Party A to Party B as per terms and conditions stipulated in this Agreement.<br><br>In the Agreement, a reference to a statute or statutory provision includes a reference to that statute or statutory provision as modified, consolidated and/or re-enacted from time to time; and any subordinate legislation made under that statute or statutory provision. The Agreement shall be binding on, and ensure to the benefit of, the parties to this Agreement and their respective personal representatives, successors and permitted assigns, and references to any party shall include that party's personal representatives, successors and permitted assigns. A reference to writing or written includes email.<br><br>Any obligation on a party not to do something includes an obligation not to allow that thing to be done. Any words following the terms “including”, “includes”, “in particular” or any similar expression shall be construed as illustrative and shall not limit the sense of the words, description, definition, phrase or term preceding those terms.",
    'Liability and Indemnification': "The first party, hereby, Party A and the other party, known as Party B, agree as stated. In the event of an occurrence due to negligent or wrongful acts by either Party A or Party B, the responsible party shall bear the onus to compensate for any damage infliction, losses, costs, expenses, claims, actions or proceedings which may be incurred by the other party. This includes all indirect, consequential and incidental damages and may comprise any court costs or fees for legal services. <br><br>Furthermore, Party A and Party B both agree that, circumstances prevailing, upon receipt of an impending claim or demand, to duly notify the other party in written form with full details of the matter. The responsible party shall, without delaying and at their own expense, either resist any impending litigation in conjunction with the other party or settle, keeping the other party's interest in consideration, the claim or demand.<br><br>In addition, both parties should note that they should implement all reasonable measures to mitigate the damages resulting from any claim or demand.  In no event shall Party A or Party B be liable to others for any losses or damages for an event that is beyond their reasonable control. <br><br>The clauses mentioned herein, shall not expire upon termination or conclusion of our agreement, but shall remain in vigor and continue to be binding upon both parties. Claims or actions involving a third party affiliated with either Party A or Party B also fall into this accord.<br><br>Both parties in acceptance have understood and agreed to adhere to the terms set out.",
    'Parties to the Agreement': 'This agreement is entered into by and between the first party, hereinafter referred to as Party A, duly represented by its legal representative and having its registered place of business at the address provided, and the second party, hereinafter referred to as Party B, duly represented by its legal representative and having its registered place of business at the address provided. Both Party A and Party B may individually be referred to as Party and collectively as Parties in this agreement.',
    'Recitals': 'The first party, with registered address as mentioned hereafter, is a company incorporated under the laws of the United Kingdom and, as such, has the ability to engage in the obligations set out in this agreement.<br><br>The second party, also with a registered address detailed below, operates under the laws of the United Kingdom, possessing similar capabilities to engage in the obligations agreed upon in this legal document.<br><br>Both parties have expressed their keenness and outright intention to enter into this agreement, to mutually benefit from the ensuing business process, and to contribute to its successful implementation.<br><br>Aligning with the mutual interest of both parties, this agreement is being discussed, drafted and agreed upon freely and willingly, without any undue influence, coaction or duress, undisclosed terms or conditions, or any type of prevarication.<br><br>Both parties have been given adequate opportunity to take professional legal advice, examine, and understand all aspects of this agreement, and all its implications and bindings.<br><br>Each party guarantees and establishes, to the best of their knowledge, that they have not been coerced into signing this agreement and they fully understand and agree to all the terms and conditions herein.<br><br>The parties agree to abide by all these agreed terms, and mutually yet individually warrant that they have and will continue to have the required legal ability to enter into this binding agreement.<br><br>Lastly, this is a legally binding document and all the undersigned parties are voluntarily proceeding with full knowledge of the implications and consequences set out in this agreement.',
    'Rights and Obligations': 'The parties involved in this agreement are accorded certain rights and are mandated to adhere to several obligations. <br><br>For the first party, they have the liberty to fully procure all benefits that arise from this agreement. However, they are expected to pay any financial costs accrued as enacted by the terms and conditions enclosed herewith. They are also obligated to provide all the necessary information to facilitate a smooth operation in the agreed terms as well as ensuring a conducive working environment for all parties involved. Any act deemed inappropriate or damaging might result in legal action.<br><br>The second party has the right to all claim to all benefits as per the execution of this agreement. Their obligations encompass satisfactory execution of their tasks as agreed under this agreement. They must equally maintain a professional and ethical approach in all their dealings and provide the necessary support to the first party as per the agreement. <br><br>Both parties must adhere to the rules set on confidentiality and must not disclose any information deemed confidential under the terms of this agreement, except to the extent permitted by law. <br><br>The parties should notify each other of any relevant changes in their respective circumstances that may potentially affect the validity or execution of this agreement.<br><br>The agreement bestows the right of termination to both parties in case there is a breach of any clauses or underperformance. The party desiring to terminate this agreement is required to issue a notice in writing to the other party. The termination shall not affect any legal rights, obligations or liabilities accrued under the agreement up to the termination.<br><br>The agreement ensures that each right or remedy that the parties have under this agreement is without prejudice to any other right or remedy that may exist.<br><br>It is important that both parties comply strictly with all laws, regulations, and orders applicable to the activities under this agreement.<br><br>Non-compliance with any of the aforementioned conditions may lead to penalties, sanctions, or the termination of the agreement.',
    'Termination and Consequences.': 'Either party may terminate this agreement by providing written notice to the other party. Such termination will become effective 30 days after receipt of the notice. In the event of termination, the responsibilities of the parties, accrued prior to the termination date, will remain in effect. <br><br>Should the agreement be terminated by either party, any fees owed by one party to the other at the date of termination must be settled within 45 days. Any delays may result in the imposition of interest charges, as per standard commercial rates.<br><br>In the event of termination, each party must return or destroy all confidential information received from the other party, in whatever form or medium, and cease all further use of such confidential information. The obligation of confidentiality and the restrictions on use of confidential information will survive the termination and continue in full force and effect.<br><br>No party shall be liable to the other for damages of any sort resulting solely from terminating this agreement in accordance with its terms. However, termination will not relieve either party of any obligations incurred prior to the termination, which obligations will survive the termination. <br><br>In case of termination of this agreement, the parties will have no further obligations under this agreement except for such obligations that by their nature are intended to survive termination, including, but not limited to, obligations concerning intellectual property, confidentiality, and dispute resolution. <br><br>Any dispute arising out of or in connection with the termination of this agreement, including any dispute regarding the existence, validity or termination of this agreement, shall be referred to and finally resolved by arbitration under the rules of the applicable law. The arbitration proceedings shall be conducted in English. <br><br>Please consult a professional legal advisor for further clarification or advice. This document is a guideline and does not constitute legal advice. Legal liability is thus disclaimed for accuracy, completeness, or adequacy of the information provided herein.',
    'Terms and Conditions': 'Both parties agree that this Agreement is the complete and exclusive statement of the mutual understanding of the parties and supersedes and cancels all previous written and oral agreements, communications and other understandings relating to the subject matter of this Agreement, and that all modifications must be in a writing signed by both parties, except as otherwise provided herein.<br><br>The services will only be used for lawful purposes and in a manner which does not infringe the rights, or restrict, or inhibit the use and enjoyment of the service by any third party. The client must not use our services for illegal purposes or in any manner inconsistent with the regulations of any applicable local, state and national laws.<br><br>Neither party shall be liable to the other for any failure to perform any obligation under any Agreement which is due to an event beyond the control of such party including but not limited to any Acts of God, terrorism, war, political insurgence, insurrection, riot, civil unrest, act of civil or military authority, uprising, earthquake, flood or any other natural or man-made eventuality outside of our control, which causes the termination of an agreement or contract entered into, nor which could have been reasonably foreseen.<br><br>Each party represents and warrants that it has the legal power and authority to enter into this Agreement. Both parties are to keep any information gained from the use of the services confidential and must not disclose it to any third party without the prior written consent of the other party. If these conditions are breached, the party in breach must immediately remedy the breach at its own expense.<br><br>Both parties must indemnify and hold harmless, each other against all claims, actions, proceedings, losses, damages, expenses and all costs arising out of or in connection with the client’s use of the services, the client’s non-compliance with our guidelines, or the client’s breach of these terms and conditions.<br><br>All notices to be given under this Agreement will be in writing and will be sent to the address of the recipient set out in this Agreement or such other address as the recipient may designate by notice given in accordance with this clause.<br><br>This Agreement is made pursuant to the laws of England and Wales and the parties agree to submit to the non-exclusive jurisdiction of the English courts.<br><br>Any dispute arising under or in connection with this Agreement shall be referred to mediation by a single mediator nominated with the consent of both parties. <br><br>This Agreement will not be assigned, transferred, sub-licensed, or charged by either party without the prior written consent of the other party. <br><br>A waiver by us of any terms of the Agreement will not in any way constitute a legal or equitable waiver of any other terms. If any provision of the Agreement is found by a court of competent jurisdiction to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary so that this Agreement shall otherwise remain in full force and effect and enforceable.'
}

SEND_CONTRACT_TO_SIGNEE_EMAIL_TEMPLATE = '''Hi <span class="restricted-editing-exception">{signee_name}</span>, <br><br> I am writing to inform you that I have sent a document your way that requires your attention and electronic signature. <br><br> To access the document and initiate the signing process, please click on the following button: <span class="restricted-editing-exception"><button type="button" style="background:#14e4ea;border: none;padding: 5px;border-radius: 4px"><a href="{contract_link}" style="color:white;text-decoration: none">Contract</a></button></span><br><br>Or using this link: <a class="restricted-editing-exception" href="{contract_link}" target="_blank">{contract_link}</a><br><br> Your prompt review and signature are greatly appreciated. If you have any questions or need further clarification regarding the content or the signing process, please do not hesitate to reach out to me at <span class="restricted-editing-exception">{contact_information}</span>. <br><br> Once you have completed the e-signature process, you will receive a confirmation email. This will help ensure a smooth and efficient workflow. <br><br> Thank you for your cooperation in this matter. I look forward to receiving the signed document at your earliest convenience.'''
CONTRACT_CANCELLED = '''Hi <span class="restricted-editing-exception">{name}</span>, <br><br> We would like to inform you that the e-contract has been cancelled due to unforeseen circumstances. <br><br> Any previous agreements related to this e-contract are now null and void. We will handle the necessary administrative tasks to ensure a smooth cancellation process. <br><br> We appreciate your understanding and cooperation during this process. If you have any further instructions or specific requirements related to this cancellation, please let us know, and we will work with you to ensure your needs are met. <br><br> Thank you for your attention to this matter. <br><br> Sincerely'''
CONTRACT_SIGNING_SIGNEE_STATUS_COMPLETE = '''Hi <span class="restricted-editing-exception">{name}</span>, <br><br> I am pleased to inform you that we have received your electronic signature on the document we recently sent for review and approval. <br><br> Your prompt attention to this matter is greatly appreciated, and I'm delighted to confirm that the document status is now complete. This signifies that all necessary signatures have been obtained, and the document is fully executed. <br><br> Thank you once again for your cooperation and timely response. We look forward to continuing our successful collaboration.'''
SEND_REMINDER_TO_SIGNEE = '''Hi <span class="restricted-editing-exception">{name}</span>, <br><br> This is a friendly reminder regarding the document that requires your review and electronic signature. <br><br> As previously communicated, an important document awaits your attention. You can access the document and initiate the signing process by clicking on the following button: <span class="restricted-editing-exception"><button type="button" style="background:#14e4ea;border: none;padding: 5px;border-radius: 4px"><a href="{contract_link}" style="color:white;text-decoration: none">Contract</a></button></span><br><br>Or using this link: <a class="restricted-editing-exception" href="{contract_link}" target="_blank">{contract_link}</a> <br><br> Your review and signature on this document are crucial to our ongoing [project/collaboration/transaction]. We kindly request that you complete this process at your earliest convenience to ensure that there are no delays in our progress. <br><br> Your prompt action on this matter is greatly appreciated, and we thank you for your cooperation.'''


CurrencyCode = {
    'Afghanistan': 'AFN',
    'Albania': 'ALL',
    'Algeria': 'DZD',
    'Angola': 'AOA',
    'Anguilla': 'XCD',
    'Antigua and Barbuda': 'XCD',
    'Argentina': 'ARS',
    'Armenia': 'AMD',
    'Aruba': 'AWG',
    'Australia': 'AUD',
    'Austria': 'EUR',
    'Azerbaijan': 'AZN',
    'Bahamas': 'BSD',
    'Bahrain': 'BHD',
    'Bangladesh': 'BDT',
    'Barbados': 'BBD',
    'Belarus': 'BYN',
    'Belarus (Old)': 'BYR',
    'Belgium': 'EUR',
    'Belize': 'BZD',
    'Benin': 'XOF',
    'Bermuda': 'BMD',
    'Bhutan': 'BTN',
    'Bolivia': 'BOB',
    'Bosnia and Herzegovina': 'BAM',
    'Botswana': 'BWP',
    'Brazil': 'BRL',
    'Brunei': 'BND',
    'Bulgaria': 'BGN',
    'Burkina Faso': 'XOF',
    'Burundi': 'BIF',
    'CFP franc': 'XPF',
    'Cambodia': 'KHR',
    'Cameroon': 'XAF',
    'Canada': 'CAD',
    'Cape Verde': 'CVE',
    'Cayman Islands': 'KYD',
    'Central African Republic': 'XAF',
    'Chad': 'XAF',
    'Chile': 'CLP',
    'China': 'CNY',
    'Colombia': 'COP',
    'Comoros': 'KMF',
    'Congo, Republic of the': 'XAF',
    'Costa Rica': 'CRC',
    'Croatia': 'HRK',
    'Cuba': 'CUP',
    'Cyprus': 'EUR',
    'Czech Republic': 'CZK',
    'Côte d’Ivoire': 'XOF',
    'Democratic Republic of the Congo': 'CDF',
    'Denmark': 'DKK',
    'Djibouti': 'DJF',
    'Dominica': 'XCD',
    'Dominican Republic': 'DOP',
    'East Timor (Timor-Leste)': 'USD',
    'Ecuador': 'USD',
    'Egypt': 'EGP',
    'El Salvador': 'USD',
    'Equatorial Guinea': 'XAF',
    'Eritrea': 'ERN',
    'Estonia': 'EUR',
    'Eswatini': 'SZL',
    'Ethiopia': 'ETB',
    'Falkland Islands': 'FKP',
    'Fiji': 'FJD',
    'Finland': 'EUR',
    'France': 'EUR',
    'Gabon': 'XAF',
    'Gambia': 'GMD',
    'Georgia': 'GEL',
    'Germany': 'EUR',
    'Ghana': 'GHS',
    'Gibraltar': 'GIP',
    'Greece': 'EUR',
    'Greenland': 'DKK',
    'Grenada': 'XCD',
    'Guatemala': 'GTQ',
    'Guernsey': 'GGP',
    'Guinea': 'GNF',
    'Guinea-Bissau': 'XOF',
    'Guyana': 'GYD',
    'Haiti': 'HTG',
    'Honduras': 'HNL',
    'Hong Kong': 'HKD',
    'Hungary': 'HUF',
    'Iceland': 'ISK',
    'India': 'INR',
    'Indonesia': 'IDR',
    'Iran': 'IRR',
    'Iraq': 'IQD',
    'Ireland': 'EUR',
    'Isle of Man': 'IMP',
    'Israel': 'ILS',
    'Italy': 'EUR',
    'Jamaica': 'JMD',
    'Japan': 'JPY',
    'Jersey': 'JEP',
    'Jordan': 'JOD',
    'Kazakhstan': 'KZT',
    'Kenya': 'KES',
    'Kiribati': 'AUD',
    'Kosovo': 'EUR',
    'Kuwait': 'KWD',
    'Kyrgyzstan': 'KGS',
    'Laos': 'LAK',
    'Latvia': 'LVL',
    'Lebanon': 'LBP',
    'Lesotho': 'LSL',
    'Liberia': 'LRD',
    'Libya': 'LYD',
    'Liechtenstein': 'CHF',
    'Lithuania': 'LTL',
    'Luxembourg': 'EUR',
    'Macau': 'MOP',
    'Madagascar': 'MGA',
    'Malawi': 'MWK',
    'Malaysia': 'MYR',
    'Maldives': 'MVR',
    'Mali': 'XOF',
    'Malta': 'EUR',
    'Marshall Islands': 'USD',
    'Mauritania': 'MRO',
    'Mauritius': 'MUR',
    'Mexico': 'MXN',
    'Micronesia, Federated States of': 'USD',
    'Moldova': 'MDL',
    'Monaco': 'EUR',
    'Mongolia': 'MNT',
    'Montserrat': 'XCD',
    'Morocco': 'MAD',
    'Mozambique': 'MZN',
    'Myanmar (Burma)': 'MMK',
    'Namibia': 'NAD',
    'Nauru': 'AUD',
    'Nepal': 'NPR',
    'Netherlands': 'Euro',
    'Netherlands Antilles': 'ANG',
    'New Zealand': 'NZD',
    'Nicaragua': 'NIO',
    'Niger': 'XOF',
    'Nigeria': 'NGN',
    'North Korea': 'KPW',
    'North Macedonia': 'MKD',
    'Norway': 'NOK',
    'Oman': 'OMR',
    'Pakistan': 'PKR',
    'Palau': 'USD',
    'Panama': 'PAB',
    'Papua New Guinea': 'PGK',
    'Paraguay': 'PYG',
    'Peru': 'PEN',
    'Philippines': 'PHP',
    'Poland': 'PLN',
    'Portugal': 'EUR',
    'Qatar': 'QAR',
    'Romania': 'RON',
    'Russia': 'RUB',
    'Rwanda': 'RWF',
    'Saint Helena': 'SHP',
    'Saint Kitts and Nevis': 'XCD',
    'Saint Lucia': 'XCD',
    'Saint Vincent and the Grenadines': 'XCD',
    'Samoa': 'WST',
    'San Marino': 'EUR',
    'Sao Tome and Principe': 'STN',
    'Saudi Arabia': 'SAR',
    'Senegal': 'XOF',
    'Serbia': 'RSD',
    'Seychelles': 'SCR',
    'Sierra Leone': 'SLE',
    'Sierra Leone (old)': 'SLL',
    'Singapore': 'SGD',
    'Slovakia': 'EUR',
    'Slovenia': 'EUR',
    'Solomon Islands': 'SBD',
    'Somalia': 'SOS',
    'South Africa': 'ZAR',
    'South Korea': 'KRW',
    'South Sudan': 'SSP',
    'Spain': 'EUR',
    'Sri Lanka': 'LKR',
    'Sudan': 'SDG',
    'Suriname': 'SRD',
    'Sweden': 'SEK',
    'Switzerland': 'CHF',
    'Syria': 'SYP',
    'Taiwan': 'TWD',
    'Tajikistan': 'TJS',
    'Tanzania': 'TZS',
    'Thailand': 'THB',
    'Togo': 'XOF',
    'Tonga': 'TOP',
    'Trinidad and Tobago': 'TTD',
    'Tunisia': 'TND',
    'Turkey': 'TRY',
    'Turkmenistan': 'TMT',
    'Tuvalu': 'AUD',
    'USA': 'USD',
    'Uganda': 'UGX',
    'Ukraine': 'UAH',
    'United Arab Emirates': 'AED',
    'United Kingdom': 'GBP',
    'Uruguay': 'UYU',
    'Uzbekistan': 'UZS',
    'Vanuatu': 'VUV',
    'Vatican City': 'EUR',
    'Venezuela': 'VES',
    'Venezuela (Old)': 'VEF',
    'Vietnam': 'VND',
    'Yemen': 'YER',
    'Zambia': 'ZMW',
    'Zimbabwe': 'ZWL'
}
