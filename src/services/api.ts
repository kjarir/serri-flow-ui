const API_BASE_URL = 'http://localhost:8000';

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  processed: boolean;
  created_at: string;
  query_count: number;
}

export interface QueryResponse {
  answer: string;
  confidence_score?: number;
  iteration_count: number;
  feedback_options: string[];
}

export interface UploadResponse {
  doc_id: number;
  filename: string;
  message: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-secret-api-key-here', // This should be configurable
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Document Bot APIs
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/document-bot/upload-doc`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer your-secret-api-key-here',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }

    return await response.json();
  }

  async askQuery(docId: number, query: string): Promise<QueryResponse> {
    return this.request<QueryResponse>('/api/document-bot/ask-query', {
      method: 'POST',
      body: JSON.stringify({ doc_id: docId, query }),
    });
  }

  async submitFeedback(queryId: number, feedback: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/document-bot/feedback', {
      method: 'POST',
      body: JSON.stringify({ query_id: queryId, feedback }),
    });
  }

  async getDocuments(): Promise<Document[]> {
    return this.request<Document[]>('/api/document-bot/documents');
  }

  async getDocumentQueries(docId: number): Promise<any[]> {
    return this.request<any[]>(`/api/document-bot/queries/${docId}`);
  }

  async getDocumentLogs(docId: number): Promise<any[]> {
    return this.request<any[]>(`/api/document-bot/logs/${docId}`);
  }

  // Chatbot APIs
  async chat(message: string, leadId?: number): Promise<{
    response: string;
    intent?: string;
    lead_id?: number;
    next_actions?: string[];
  }> {
    return this.request('/api/chatbot/chat', {
      method: 'POST',
      body: JSON.stringify({ message, lead_id: leadId }),
    });
  }

  async createLead(leadData: {
    email: string;
    name?: string;
    company?: string;
    industry?: string;
    company_size?: string;
    role?: string;
    decision_making_power?: string;
    interest_level?: string;
    phone?: string;
  }): Promise<any> {
    return this.request('/api/chatbot/lead', {
      method: 'POST',
      body: JSON.stringify(leadData),
    });
  }

  async scheduleDemo(leadId: number, preferredDate?: string): Promise<{
    calendly_link: string;
    event_id?: string;
    message: string;
  }> {
    return this.request('/api/chatbot/schedule-demo', {
      method: 'POST',
      body: JSON.stringify({ lead_id: leadId, preferred_date: preferredDate }),
    });
  }

  async handleObjection(objectionType: string, leadId?: number): Promise<{
    response: string;
    follow_up_questions?: string[];
  }> {
    return this.request('/api/chatbot/objection', {
      method: 'POST',
      body: JSON.stringify({ objection_type: objectionType, lead_id: leadId }),
    });
  }

  async sendFollowUp(leadId: number, followUpType: string): Promise<{
    message: string;
    sent: boolean;
    method: string;
  }> {
    return this.request('/api/chatbot/followup', {
      method: 'POST',
      body: JSON.stringify({ lead_id: leadId, follow_up_type: followUpType }),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
