import { Bot, FileText, Users, BarChart3, Zap, Shield } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

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
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <section className="section-padding bg-background">
      <div className="section-container">
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Everything You Need to Automate Customer Support
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powerful features designed to transform your customer service from reactive to proactive, 
            while maintaining the personal touch your customers love.
          </p>
        </motion.div>
        
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              variants={itemVariants}
              whileHover={{ 
                y: -10, 
                scale: 1.02,
                transition: { duration: 0.2 }
              }}
            >
              <Card className="feature-card hover:shadow-glow group h-full">
                <CardHeader>
                  <motion.div 
                    className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors"
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <feature.icon className="h-6 w-6 text-primary" />
                  </motion.div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};