import { Star, Quote } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const testimonials = [
  {
    id: 1,
    name: "Sarah Chen",
    role: "Head of Customer Success",
    company: "TechFlow Inc.",
    rating: 5,
    content: "Serri transformed our customer support overnight. We went from 6-hour response times to instant, accurate answers. Our team can now focus on complex issues while Serri handles the routine questions perfectly.",
    avatar: "/api/placeholder/40/40"
  },
  {
    id: 2,
    name: "Marcus Johnson",
    role: "Founder & CEO",
    company: "StartupLabs",
    rating: 5,
    content: "The lead qualification feature is a game-changer. Serri identifies high-quality prospects and schedules demos automatically. We've seen a 300% increase in qualified leads since implementation.",
    avatar: "/api/placeholder/40/40"
  },
  {
    id: 3,
    name: "Emily Rodriguez",
    role: "VP of Operations",
    company: "GrowthCorp",
    rating: 5,
    content: "Implementation was seamless, and the document training feature is incredibly powerful. Our knowledge base is now accessible 24/7, and customers get consistent, accurate information every time.",
    avatar: "/api/placeholder/40/40"
  }
];

export const TestimonialsSection = () => {
  return (
    <section className="section-padding bg-background">
      <div className="section-container">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Trusted by Forward-Thinking Companies
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            See how businesses like yours are transforming their customer support 
            and accelerating growth with Serri AI.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <Card 
              key={testimonial.id}
              className="feature-card animate-fade-in hover:shadow-glow"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                
                <div className="relative mb-6">
                  <Quote className="absolute -top-2 -left-2 h-8 w-8 text-primary/20" />
                  <p className="text-muted-foreground leading-relaxed pl-6">
                    "{testimonial.content}"
                  </p>
                </div>
                
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarImage src={testimonial.avatar} alt={testimonial.name} />
                    <AvatarFallback>
                      {testimonial.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {testimonial.role} at {testimonial.company}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="text-center mt-12 animate-fade-in">
          <div className="flex items-center justify-center gap-8 opacity-60">
            <div className="text-2xl font-bold">TechFlow</div>
            <div className="text-2xl font-bold">StartupLabs</div>
            <div className="text-2xl font-bold">GrowthCorp</div>
            <div className="text-2xl font-bold">InnovateCo</div>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            Join 500+ companies already using Serri AI
          </p>
        </div>
      </div>
    </section>
  );
};