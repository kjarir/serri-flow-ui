import { useState } from "react";
import { Upload, FileText, MessageSquare, ThumbsUp, ThumbsDown, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DocumentUpload } from "@/components/DocumentUpload";
import { QueryInterface } from "@/components/QueryInterface";
import { FeedbackPanel } from "@/components/FeedbackPanel";

const Dashboard = () => {
  const [uploadedDocs, setUploadedDocs] = useState<Array<{
    id: string;
    name: string;
    type: string;
    size: string;
    extractedText: string;
  }>>([]);

  const [queries, setQueries] = useState<Array<{
    id: string;
    query: string;
    response: string;
    feedback?: 'helpful' | 'not-helpful' | 'too-vague';
    timestamp: Date;
  }>>([]);

  return (
    <div className="min-h-screen bg-subtle-gradient">
      <header className="border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
        <div className="section-container">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <MessageSquare className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Support Bot Dashboard</h1>
                <p className="text-sm text-muted-foreground">Train your AI with documents</p>
              </div>
            </div>
            <Button variant="outline" asChild>
              <a href="/">← Back to Landing</a>
            </Button>
          </div>
        </div>
      </header>

      <main className="section-container py-8">
        <Tabs defaultValue="upload" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="upload">Upload Documents</TabsTrigger>
            <TabsTrigger value="query">Query & Test</TabsTrigger>
            <TabsTrigger value="feedback">Feedback & Training</TabsTrigger>
            <TabsTrigger value="logs">Query Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="animate-fade-in">
            <div className="grid gap-6 md:grid-cols-2">
              <DocumentUpload 
                onUpload={(docs) => setUploadedDocs(prev => [...prev, ...docs])}
              />
              
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Uploaded Documents ({uploadedDocs.length})
                  </CardTitle>
                  <CardDescription>
                    Documents that have been processed and indexed
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {uploadedDocs.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No documents uploaded yet
                      </p>
                    ) : (
                      uploadedDocs.map((doc) => (
                        <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <div>
                              <p className="font-medium text-sm">{doc.name}</p>
                              <p className="text-xs text-muted-foreground">{doc.size}</p>
                            </div>
                          </div>
                          <Badge variant="secondary">{doc.type.toUpperCase()}</Badge>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="query" className="animate-fade-in">
            <QueryInterface 
              onQuery={(query, response) => {
                const newQuery = {
                  id: Date.now().toString(),
                  query,
                  response,
                  timestamp: new Date()
                };
                setQueries(prev => [newQuery, ...prev]);
              }}
            />
          </TabsContent>

          <TabsContent value="feedback" className="animate-fade-in">
            <FeedbackPanel 
              queries={queries}
              onFeedback={(queryId, feedback) => {
                setQueries(prev => prev.map(q => 
                  q.id === queryId ? { ...q, feedback } : q
                ));
              }}
            />
          </TabsContent>

          <TabsContent value="logs" className="animate-fade-in">
            <Card>
              <CardHeader>
                <CardTitle>Query History</CardTitle>
                <CardDescription>
                  All queries and responses with feedback status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {queries.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      No queries yet. Start by testing your bot in the Query & Test tab.
                    </p>
                  ) : (
                    queries.map((query) => (
                      <div key={query.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium">Query:</p>
                            <p className="text-sm text-muted-foreground">{query.query}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            {query.feedback && (
                              <Badge 
                                variant={query.feedback === 'helpful' ? 'default' : 'destructive'}
                              >
                                {query.feedback}
                              </Badge>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {query.timestamp.toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="font-medium">Response:</p>
                          <p className="text-sm bg-muted rounded p-2">{query.response}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;