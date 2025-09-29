import { MessageCircle, Mail, Phone, MapPin, Twitter, Linkedin, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const Footer = () => {
  return (
    <footer className="bg-card border-t">
      <div className="section-container py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <MessageCircle className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">Serri AI</span>
            </div>
            <p className="text-muted-foreground">
              Transform your customer support with AI-powered intelligence. 
              Automate responses, qualify leads, and deliver exceptional experiences.
            </p>
            <div className="flex gap-2">
              <Button variant="ghost" size="icon">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Linkedin className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Github className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <div className="space-y-2">
              <a href="#features" className="block text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#pricing" className="block text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </a>
              <a href="/dashboard" className="block text-muted-foreground hover:text-foreground transition-colors">
                Dashboard
              </a>
              <a href="#integrations" className="block text-muted-foreground hover:text-foreground transition-colors">
                Integrations
              </a>
              <a href="#api" className="block text-muted-foreground hover:text-foreground transition-colors">
                API Docs
              </a>
            </div>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <div className="space-y-2">
              <a href="#about" className="block text-muted-foreground hover:text-foreground transition-colors">
                About Us
              </a>
              <a href="#careers" className="block text-muted-foreground hover:text-foreground transition-colors">
                Careers
              </a>
              <a href="#blog" className="block text-muted-foreground hover:text-foreground transition-colors">
                Blog
              </a>
              <a href="#contact" className="block text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </a>
              <a href="#privacy" className="block text-muted-foreground hover:text-foreground transition-colors">
                Privacy Policy
              </a>
            </div>
          </div>

          {/* Contact & Newsletter */}
          <div>
            <h3 className="font-semibold mb-4">Stay Updated</h3>
            <p className="text-muted-foreground text-sm mb-4">
              Get the latest updates on AI features and product announcements.
            </p>
            <div className="flex gap-2 mb-6">
              <Input 
                placeholder="Enter your email" 
                className="flex-1"
              />
              <Button>Subscribe</Button>
            </div>
            
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <span>hello@serri.ai</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>San Francisco, CA</span>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-muted-foreground text-sm">
            © 2024 Serri AI. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm text-muted-foreground mt-4 md:mt-0">
            <a href="#terms" className="hover:text-foreground transition-colors">
              Terms of Service
            </a>
            <a href="#privacy" className="hover:text-foreground transition-colors">
              Privacy Policy
            </a>
            <a href="#cookies" className="hover:text-foreground transition-colors">
              Cookie Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};