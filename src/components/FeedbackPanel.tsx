import { ThumbsUp, ThumbsDown, AlertCircle, MessageCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Query {
  id: string;
  query: string;
  response: string;
  feedback?: 'helpful' | 'not-helpful' | 'too-vague';
  timestamp: Date;
}

interface FeedbackPanelProps {
  queries: Query[];
  onFeedback: (queryId: string, feedback: 'helpful' | 'not-helpful' | 'too-vague') => void;
}

export const FeedbackPanel = ({ queries, onFeedback }: FeedbackPanelProps) => {
  const getFeedbackStats = () => {
    const total = queries.length;
    const helpful = queries.filter(q => q.feedback === 'helpful').length;
    const notHelpful = queries.filter(q => q.feedback === 'not-helpful').length;
    const tooVague = queries.filter(q => q.feedback === 'too-vague').length;
    const pending = total - helpful - notHelpful - tooVague;
    
    return { total, helpful, notHelpful, tooVague, pending };
  };

  const stats = getFeedbackStats();

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">{stats.total}</div>
            <div className="text-xs text-muted-foreground">Total Queries</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">{stats.helpful}</div>
            <div className="text-xs text-muted-foreground">Helpful</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-destructive">{stats.notHelpful}</div>
            <div className="text-xs text-muted-foreground">Not Helpful</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">{stats.tooVague}</div>
            <div className="text-xs text-muted-foreground">Too Vague</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-muted-foreground">{stats.pending}</div>
            <div className="text-xs text-muted-foreground">Pending</div>
          </CardContent>
        </Card>
      </div>

      {/* Feedback Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Response Feedback
          </CardTitle>
          <CardDescription>
            Review and provide feedback on bot responses to improve training
          </CardDescription>
        </CardHeader>
        <CardContent>
          {queries.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No queries to review yet.</p>
              <p className="text-xs">Test your bot in the Query & Test tab first.</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {queries.map((query) => (
                <div
                  key={query.id}
                  className="border rounded-lg p-4 space-y-4 hover:bg-muted/25 transition-colors"
                >
                  {/* Query */}
                  <div>
                    <div className="flex items-start justify-between mb-2">
                      <p className="font-medium text-sm">User Query:</p>
                      <div className="flex items-center gap-2">
                        {query.feedback && (
                          <Badge 
                            variant={
                              query.feedback === 'helpful' 
                                ? 'default' 
                                : query.feedback === 'not-helpful' 
                                ? 'destructive' 
                                : 'secondary'
                            }
                          >
                            {query.feedback.replace('-', ' ')}
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {query.timestamp.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm bg-muted/50 rounded p-2">{query.query}</p>
                  </div>

                  {/* Response */}
                  <div>
                    <p className="font-medium text-sm mb-2">Bot Response:</p>
                    <p className="text-sm bg-primary/5 rounded p-2 border-l-2 border-primary">
                      {query.response}
                    </p>
                  </div>

                  {/* Feedback Buttons */}
                  <div className="flex items-center justify-between pt-2 border-t">
                    <p className="text-sm text-muted-foreground">
                      Was this response helpful?
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant={query.feedback === 'helpful' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => onFeedback(query.id, 'helpful')}
                        className="flex items-center gap-1"
                      >
                        <ThumbsUp className="h-3 w-3" />
                        Helpful
                      </Button>
                      <Button
                        variant={query.feedback === 'not-helpful' ? 'destructive' : 'outline'}
                        size="sm"
                        onClick={() => onFeedback(query.id, 'not-helpful')}
                        className="flex items-center gap-1"
                      >
                        <ThumbsDown className="h-3 w-3" />
                        Not Helpful
                      </Button>
                      <Button
                        variant={query.feedback === 'too-vague' ? 'secondary' : 'outline'}
                        size="sm"
                        onClick={() => onFeedback(query.id, 'too-vague')}
                        className="flex items-center gap-1"
                      >
                        <AlertCircle className="h-3 w-3" />
                        Too Vague
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};