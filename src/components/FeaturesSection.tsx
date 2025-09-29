import { Bot, FileText, Users, BarChart3, Zap, Shield } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Bot,
    title: "AI Document Training",
    description: "Upload your knowledge base and train your AI to provide accurate, contextual responses from your existing documentation."
  },
  {
    icon: Users,
    title: "Lead Qualification",
    description: "Automatically qualify leads with intelligent conversations that capture key information and route prospects appropriately."
  },
  {
    icon: FileText,
    title: "Smart Content Processing",
    description: "Advanced NLP processes PDFs, documents, and text files to extract and index relevant information for instant retrieval."
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "Track performance metrics, conversation quality, and user satisfaction with comprehensive analytics and reporting."
  },
  {
    icon: Zap,
    title: "Real-time Responses",
    description: "Lightning-fast AI responses that improve over time through machine learning and continuous feedback loops."
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Bank-level security with end-to-end encryption, SOC 2 compliance, and robust data protection protocols."
  }
];

export const FeaturesSection = () => {
  return (
    <section className="section-padding bg-background">
      <div className="section-container">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Everything You Need to Automate Customer Support
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powerful features designed to transform your customer service from reactive to proactive, 
            while maintaining the personal touch your customers love.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card 
              key={feature.title} 
              className="feature-card animate-fade-in hover:shadow-glow group"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};