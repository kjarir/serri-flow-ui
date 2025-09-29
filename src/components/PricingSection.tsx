import { Check, Sparkles, Building, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const plans = [
  {
    name: "Starter",
    price: "$99",
    period: "/month",
    description: "Perfect for small teams getting started with AI support",
    icon: Rocket,
    features: [
      "Up to 1,000 conversations/month",
      "5 document uploads",
      "Basic chatbot widget",
      "Email support",
      "Standard analytics",
      "Lead capture forms"
    ],
    popular: false
  },
  {
    name: "Professional",
    price: "$299",
    period: "/month",
    description: "Ideal for growing businesses with advanced needs",
    icon: Sparkles,
    features: [
      "Up to 10,000 conversations/month",
      "Unlimited document uploads",
      "Advanced AI training",
      "Priority support",
      "Custom branding",
      "Lead qualification flows",
      "Advanced analytics",
      "API access"
    ],
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "Tailored solutions for large organizations",
    icon: Building,
    features: [
      "Unlimited conversations",
      "Dedicated account manager",
      "Custom integrations",
      "SLA guarantees",
      "Advanced security",
      "Multi-language support",
      "Custom AI models",
      "White-label options"
    ],
    popular: false
  }
];

interface PricingSectionProps {
  onBookDemo: () => void;
}

export const PricingSection = ({ onBookDemo }: PricingSectionProps) => {
  return (
    <section className="section-padding subtle-gradient">
      <div className="section-container">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose the perfect plan for your business. Start free, scale as you grow, 
            and only pay for what you need.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card 
              key={plan.name}
              className={`relative feature-card animate-fade-in ${
                plan.popular 
                  ? 'ring-2 ring-primary shadow-glow scale-105' 
                  : ''
              }`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground px-4 py-1">
                    Most Popular
                  </Badge>
                </div>
              )}
              
              <CardHeader className="text-center pb-8">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <plan.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription className="text-base">
                  {plan.description}
                </CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.period}</span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-success mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button 
                  onClick={onBookDemo}
                  className={`w-full ${
                    plan.popular 
                      ? 'bg-primary hover:bg-primary/90' 
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                  size="lg"
                >
                  {plan.name === 'Enterprise' ? 'Contact Sales' : 'Start Free Trial'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="text-center mt-12 animate-fade-in">
          <p className="text-muted-foreground mb-4">
            All plans include a 14-day free trial. No credit card required.
          </p>
          <Button 
            variant="outline" 
            onClick={onBookDemo}
            className="hover:shadow-glow"
          >
            Compare All Features
          </Button>
        </div>
      </div>
    </section>
  );
};