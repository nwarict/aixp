from app.schemas.auth import Token, UserLogin, UserCreate, UserUpdate, UserResponse, TenantCreate, TenantResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, ContactCreate, ContactResponse
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.deal import DealCreate, DealUpdate, DealResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse, MessageCreate, MessageResponse
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse, KnowledgeBaseSearch
from app.schemas.connector import ConnectorCreate, ConnectorUpdate, ConnectorResponse
from app.schemas.automation import AutomationCreate, AutomationUpdate, AutomationResponse
from app.schemas.ai import AIChatRequest, AIChatResponse, AIConfigUpdate
from app.schemas.search import SearchRequest, SearchResult
from app.schemas.upload import UploadResponse
