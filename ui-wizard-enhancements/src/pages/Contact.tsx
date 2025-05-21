
import { useState } from "react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { Mail, Phone, MapPin, Send } from "lucide-react";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
    subject: "General Inquiry",
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // This would normally send the data to a server
    console.log("Form submitted:", formData);
    alert("Thanks for reaching out! We'll get back to you soon.");
    setFormData({
      name: "",
      email: "",
      message: "",
      subject: "General Inquiry",
    });
  };
  
  return (
    <>
      <Navigation />
      
      <main className="pt-16">
        <section className="bg-gradient-yoga py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-serif font-bold text-white mb-3">
              Contact Us
            </h1>
            <p className="text-white/90 text-xl max-w-2xl mx-auto">
              We'd love to hear from you
            </p>
          </div>
        </section>
        
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <div>
                <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-6">
                  Get in Touch
                </h2>
                <p className="text-yoga-slate mb-8">
                  Have questions about NYRA? Want to share your experience or suggest improvements? We're here to help and listen.
                </p>
                
                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="bg-yoga-mint p-3 rounded-full">
                      <Mail className="text-yoga-green" size={24} />
                    </div>
                    <div>
                      <h3 className="font-medium text-yoga-charcoal">Email</h3>
                      <p className="text-yoga-slate">addy.main061@gmail.com</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="bg-yoga-mint p-3 rounded-full">
                      <Phone className="text-yoga-green" size={24} />
                    </div>
                    <div>
                      <h3 className="font-medium text-yoga-charcoal">Phone</h3>
                      <p className="text-yoga-slate">+91 7983958279</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="bg-yoga-mint p-3 rounded-full">
                      <MapPin className="text-yoga-green" size={24} />
                    </div>
                    <div>
                      <h3 className="font-medium text-yoga-charcoal">Office</h3>
                      <p className="text-yoga-slate">
                        Bennett University,<br />
                        Greater Noida<br />
                        Uttar Pradesh 201310, India
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-12">
                  <h3 className="font-medium text-yoga-charcoal mb-4">Follow Us</h3>
                  <div className="flex space-x-4">
                    {["Twitter", "Instagram", "Facebook", "YouTube"].map((platform) => (
                      <a 
                        key={platform} 
                        href="#" 
                        className="bg-gray-100 hover:bg-yoga-mint text-yoga-slate hover:text-yoga-green 
                                 p-3 rounded-full transition-colors duration-200"
                      >
                        {platform.charAt(0)}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="yoga-card">
                <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-6">
                  Send Us a Message
                </h2>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-yoga-slate mb-1">
                      Your Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-yoga-green focus:border-yoga-green"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-yoga-slate mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-yoga-green focus:border-yoga-green"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-yoga-slate mb-1">
                      Subject
                    </label>
                    <select
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-yoga-green focus:border-yoga-green"
                    >
                      <option value="General Inquiry">General Inquiry</option>
                      <option value="Technical Support">Technical Support</option>
                      <option value="Feedback">Feedback</option>
                      <option value="Partnership">Partnership</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-yoga-slate mb-1">
                      Your Message
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={5}
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-yoga-green focus:border-yoga-green"
                    ></textarea>
                  </div>
                  
                  <button 
                    type="submit" 
                    className="yoga-button w-full flex items-center justify-center"
                  >
                    <Send className="mr-2" size={18} />
                    Send Message
                  </button>
                </form>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-12 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center max-w-3xl">
            <h2 className="text-2xl font-serif font-semibold text-yoga-charcoal mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-yoga-slate mb-8">
              Find quick answers to common questions about NYRA
            </p>
            
            <div className="space-y-6 text-left">
              {[
                {
                  q: "How accurate is NYRA's pose recognition?",
                  a: "NYRA's AI has been trained on thousands of poses and achieves over 95% accuracy in recognizing and analyzing common yoga postures."
                },
                {
                  q: "Can I use NYRA offline?",
                  a: "Currently, NYRA requires an internet connection to process pose recognition. We're working on an offline mode for future releases."
                },
                {
                  q: "Is my practice data private?",
                  a: "Yes, your practice data is fully encrypted and only used to improve your experience. We never share your personal information with third parties."
                }
              ].map((faq, index) => (
                <div key={index} className="yoga-card">
                  <h3 className="text-lg font-medium text-yoga-charcoal mb-2">{faq.q}</h3>
                  <p className="text-yoga-slate">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </>
  );
};

export default Contact;
