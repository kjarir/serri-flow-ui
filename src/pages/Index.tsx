import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HeroSection } from "@/components/HeroSection";
import { FeaturesSection } from "@/components/FeaturesSection";
import { PricingSection } from "@/components/PricingSection";
import { TestimonialsSection } from "@/components/TestimonialsSection";
import { Footer } from "@/components/Footer";
import { ChatbotWidget } from "@/components/ChatbotWidget";

const Index = () => {
  const [showCalendly, setShowCalendly] = useState(false);

  const handleBookDemo = () => {
    // In a real implementation, this would open Calendly or your booking system
    setShowCalendly(true);
    // Simulate Calendly opening
    window.open('https://calendly.com', '_blank');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <motion.nav 
        className="fixed top-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-sm border-b"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="section-container">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div 
                className="flex items-center space-x-2"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">S</span>
                </div>
                <span className="text-xl font-bold">Serri AI</span>
              </motion.div>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <motion.a 
                href="#features" 
                className="text-muted-foreground hover:text-foreground transition-colors"
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                Features
              </motion.a>
              <motion.a 
                href="#pricing" 
                className="text-muted-foreground hover:text-foreground transition-colors"
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                Pricing
              </motion.a>
              <motion.a 
                href="#testimonials" 
                className="text-muted-foreground hover:text-foreground transition-colors"
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                Testimonials
              </motion.a>
              <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
                <Link to="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
                  Dashboard
                </Link>
              </motion.div>
            </div>
            
            <div className="flex items-center space-x-4">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link to="/login">
                  <Button variant="ghost">Sign In</Button>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button onClick={handleBookDemo}>
                  Book Demo
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Main Content */}
      <main className="pt-16">
        <HeroSection onBookDemo={handleBookDemo} />
        <div id="features">
          <FeaturesSection />
        </div>
        <div id="testimonials">
          <TestimonialsSection />
        </div>
        <div id="pricing">
          <PricingSection onBookDemo={handleBookDemo} />
        </div>
      </main>

      <Footer />
      
      {/* Chatbot Widget */}
      <ChatbotWidget onScheduleDemo={handleBookDemo} />
    </div>
  );
};

export default Index;
