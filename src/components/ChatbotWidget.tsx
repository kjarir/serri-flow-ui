import { useState } from "react";
import { MessageCircle, X, Send, Calendar, ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  quickReplies?: string[];
}

interface ChatbotWidgetProps {
  onScheduleDemo?: () => void;
}

export const ChatbotWidget = ({ onScheduleDemo }: ChatbotWidgetProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: "Hi! I'm Serri, your AI assistant. I'm here to help you learn about our platform and see how it can transform your customer support. How can I help you today?",
      timestamp: new Date(),
      quickReplies: [
        "Tell me about Serri",
        "How can Serri help my business?",
        "Pricing information",
        "Schedule a demo"
      ]
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [leadData, setLeadData] = useState({
    industry: '',
    companySize: '',
    authority: '',
    interest: ''
  });
  const [currentFlow, setCurrentFlow] = useState<'chat' | 'qualification' | 'demo'>('chat');

  const botResponses = {
    "tell me about serri": "Serri is an advanced AI-powered customer support platform that combines document training with intelligent chatbots. We help businesses automate their customer support while maintaining high-quality, personalized responses.",
    "how can serri help my business": "Serri can help you: 1) Reduce response times by 80%, 2) Handle 24/7 customer inquiries, 3) Train on your existing knowledge base, 4) Qualify leads automatically, and 5) Scale your support without hiring more agents.",
    "pricing information": "We offer flexible pricing starting at $99/month for small teams, with enterprise options available. Our pricing includes unlimited chatbot interactions, document training, and lead qualification features.",
    "schedule a demo": "I'd love to schedule a demo for you! Let me gather some quick information to personalize your demo experience.",
    "features": "Our key features include: AI document training, conversational lead qualification, 24/7 chatbot support, integration with popular CRMs, analytics dashboard, and custom branding options.",
    "integrations": "Serri integrates with popular tools like Salesforce, HubSpot, Slack, Microsoft Teams, Zendesk, and many more through our API and Zapier connections."
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate bot response delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    let botResponse = "";
    let quickReplies: string[] = [];

    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes("demo") || lowerMessage.includes("schedule")) {
      setCurrentFlow('qualification');
      botResponse = "Great! I'd love to set up a personalized demo for you. Let me ask a few quick questions to make sure we show you the most relevant features.";
      quickReplies = ["Start qualification"];
    } else {
      // Find matching response
      const matchedKey = Object.keys(botResponses).find(key => 
        lowerMessage.includes(key.toLowerCase())
      );

      if (matchedKey) {
        botResponse = botResponses[matchedKey as keyof typeof botResponses];
      } else {
        botResponse = "That's a great question! I'd be happy to discuss that in detail during a personalized demo. Would you like me to schedule one for you?";
        quickReplies = ["Schedule a demo", "Tell me more", "Pricing information"];
      }
    }

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content: botResponse,
      timestamp: new Date(),
      quickReplies: quickReplies.length > 0 ? quickReplies : [
        "Tell me more",
        "Schedule a demo",
        "Pricing info"
      ]
    };

    setMessages(prev => [...prev, botMessage]);
    setIsTyping(false);
  };

  const handleQuickReply = (reply: string) => {
    if (reply === "Start qualification") {
      startQualification();
    } else {
      handleSendMessage(reply);
    }
  };

  const startQualification = () => {
    const qualificationMessage: Message = {
      id: Date.now().toString(),
      type: 'bot',
      content: "Perfect! Let's get started with a few questions:",
      timestamp: new Date()
    };
    setMessages(prev => [...prev, qualificationMessage]);
    
    setTimeout(() => {
      const firstQuestion: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "What industry is your company in?",
        timestamp: new Date(),
        quickReplies: ["Technology", "Healthcare", "E-commerce", "Financial Services", "Other"]
      };
      setMessages(prev => [...prev, firstQuestion]);
    }, 500);
  };

  const handleQualificationAnswer = (answer: string, question: string) => {
    handleSendMessage(answer);
    
    setTimeout(() => {
      let nextQuestion = "";
      let quickReplies: string[] = [];

      if (question.includes("industry")) {
        setLeadData(prev => ({ ...prev, industry: answer }));
        nextQuestion = "What's your company size?";
        quickReplies = ["1-10 employees", "11-50 employees", "51-200 employees", "200+ employees"];
      } else if (question.includes("company size")) {
        setLeadData(prev => ({ ...prev, companySize: answer }));
        nextQuestion = "What's your role in decision-making for customer support tools?";
        quickReplies = ["I make the final decision", "I influence the decision", "I'm researching options", "I'm an end user"];
      } else if (question.includes("decision-making")) {
        setLeadData(prev => ({ ...prev, authority: answer }));
        nextQuestion = "What's your timeline for implementing a new customer support solution?";
        quickReplies = ["Immediate (within 1 month)", "Short-term (1-3 months)", "Medium-term (3-6 months)", "Long-term (6+ months)"];
      } else if (question.includes("timeline")) {
        setLeadData(prev => ({ ...prev, interest: answer }));
        completeQualification();
        return;
      }

      const botMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: nextQuestion,
        timestamp: new Date(),
        quickReplies
      };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  const completeQualification = () => {
    setTimeout(() => {
      const completionMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: "Perfect! Based on your answers, I think Serri would be a great fit for your needs. Would you like to schedule a personalized demo to see how we can help your team?",
        timestamp: new Date(),
        quickReplies: ["Yes, schedule demo", "Send me more info first", "I have more questions"]
      };
      setMessages(prev => [...prev, completionMessage]);
      setCurrentFlow('demo');
    }, 1000);
  };

  const handleDemoSchedule = () => {
    if (onScheduleDemo) {
      onScheduleDemo();
    }
    
    const demoMessage: Message = {
      id: Date.now().toString(),
      type: 'bot',
      content: "Excellent! I'm opening our calendar for you to choose a time that works best. You'll receive a confirmation email with all the details. Looking forward to showing you how Serri can transform your customer support!",
      timestamp: new Date()
    };
    setMessages(prev => [...prev, demoMessage]);
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className="floating h-14 w-14 rounded-full shadow-glow hover:scale-110 transition-transform animate-float"
          size="icon"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="floating w-80 sm:w-96 animate-slide-up">
          <Card className="shadow-xl border-0 chat-gradient">
            <CardHeader className="flex-row items-center justify-between p-4 pb-2">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center">
                  <Sparkles className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold">Serri AI</h3>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-success rounded-full"></div>
                    <span className="text-xs text-muted-foreground">Online</span>
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>

            <CardContent className="p-0">
              {/* Messages */}
              <div className="h-80 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`chat-bubble ${
                        message.type === 'user' 
                          ? 'chat-bubble-user' 
                          : 'chat-bubble-bot'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      {message.quickReplies && message.quickReplies.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {message.quickReplies.map((reply, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                if (reply === "Schedule a demo" || reply === "Yes, schedule demo") {
                                  handleDemoSchedule();
                                } else if (currentFlow === 'qualification' && messages[messages.length - 1].content.includes("industry")) {
                                  handleQualificationAnswer(reply, "industry");
                                } else if (currentFlow === 'qualification' && messages[messages.length - 1].content.includes("company size")) {
                                  handleQualificationAnswer(reply, "company size");
                                } else if (currentFlow === 'qualification' && messages[messages.length - 1].content.includes("decision-making")) {
                                  handleQualificationAnswer(reply, "decision-making");
                                } else if (currentFlow === 'qualification' && messages[messages.length - 1].content.includes("timeline")) {
                                  handleQualificationAnswer(reply, "timeline");
                                } else {
                                  handleQuickReply(reply);
                                }
                              }}
                              className="quick-reply"
                            >
                              {reply}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="chat-bubble chat-bubble-bot">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="p-4 border-t">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage(inputValue);
                  }}
                  className="flex gap-2"
                >
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1"
                    disabled={isTyping}
                  />
                  <Button 
                    type="submit" 
                    size="icon"
                    disabled={!inputValue.trim() || isTyping}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};