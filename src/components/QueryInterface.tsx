import { useState } from "react";
import { Send, Bot, User, Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { apiService, Document } from "@/services/api";

interface QueryInterfaceProps {
  onQuery: (query: string, response: string) => void;
  documents?: Document[];
}

export const QueryInterface = ({ onQuery, documents = [] }: QueryInterfaceProps) => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [conversation, setConversation] = useState<Array<{
    id: string;
    type: 'user' | 'bot';
    message: string;
    timestamp: Date;
  }>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    // Check if we have documents to query
    if (documents.length === 0) {
      setError("Please upload at least one document before asking questions.");
      return;
    }

    // Use the first document if none is selected
    const docId = selectedDocId || documents[0].id;

    const userMessage = {
      id: `${Date.now()}-user`,
      type: 'user' as const,
      message: query,
      timestamp: new Date()
    };

    setConversation(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.askQuery(docId, query);
      
      const botMessage = {
        id: `${Date.now()}-bot`,
        type: 'bot' as const,
        message: response.answer,
        timestamp: new Date()
      };

      setConversation(prev => [...prev, botMessage]);
      onQuery(query, response.answer);
      setQuery("");
    } catch (error) {
      console.error('Query failed:', error);
      setError(error instanceof Error ? error.message : 'Failed to process query');
      
      const errorMessage = {
        id: `${Date.now()}-bot`,
        type: 'bot' as const,
        message: "I'm sorry, I encountered an error while processing your question. Please try again.",
        timestamp: new Date()
      };
      
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setConversation([]);
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="h-5 w-5" />
            Test Your Bot
          </CardTitle>
          <CardDescription>
            Ask questions to test how well your bot understands the uploaded documents
          </CardDescription>
        </CardHeader>
        <CardContent>
          {documents.length > 0 && (
            <div className="mb-4">
              <label className="text-sm font-medium mb-2 block">Select Document:</label>
              <select
                value={selectedDocId || documents[0].id}
                onChange={(e) => setSelectedDocId(Number(e.target.value))}
                className="w-full p-2 border rounded-md text-sm"
                disabled={isLoading}
              >
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename} ({doc.file_type})
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div className="mb-4 flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={documents.length === 0 ? "Upload documents first to ask questions..." : "Ask a question about your documents..."}
              className="min-h-[100px] resize-none"
              disabled={isLoading || documents.length === 0}
            />
            <div className="flex gap-2">
              <Button 
                type="submit" 
                disabled={!query.trim() || isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Ask Question
                  </>
                )}
              </Button>
              {conversation.length > 0 && (
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={clearConversation}
                  disabled={isLoading}
                >
                  Clear
                </Button>
              )}
            </div>
          </form>

          <div className="mt-4 text-xs text-muted-foreground space-y-1">
            <p>• Try asking specific questions about your documents</p>
            <p>• Test edge cases and complex queries</p>
            <p>• Use the feedback system to improve responses</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Conversation</CardTitle>
          <CardDescription>
            Live chat interface showing queries and responses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-h-[400px] overflow-y-auto">
            {conversation.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <Bot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No conversation yet.</p>
                <p className="text-xs">Ask a question to get started!</p>
              </div>
            ) : (
              conversation.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.type === 'bot' && (
                    <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                  
                  <div
                    className={`chat-bubble ${
                      message.type === 'user' 
                        ? 'chat-bubble-user' 
                        : 'chat-bubble-bot'
                    }`}
                  >
                    <p className="text-sm">{message.message}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>

                  {message.type === 'user' && (
                    <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
                <div className="chat-bubble chat-bubble-bot">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};